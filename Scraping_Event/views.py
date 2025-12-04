from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils import timezone
from .models import AmazonProduct, PriceTracker
from .serializers import AmazonProductSerializer, PriceTrackerSerializer, ScrapeProductSerializer
from .scraper import scrape_amazon_product
from .email_service import send_price_alert_email, send_tracker_confirmation_email


class AmazonProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Amazon products.
    
    Endpoints:
    - GET /api/products/ - List all products
    - POST /api/products/ - Create/scrape a new product
    - GET /api/products/{id}/ - Get product details
    - POST /api/products/scrape/ - Scrape product from URL
    """
    queryset = AmazonProduct.objects.all()
    serializer_class = AmazonProductSerializer
    permission_classes = [AllowAny]
    filterset_fields = ['asin', 'currency']
    search_fields = ['title', 'asin']

    @action(detail=False, methods=['post'], url_path='scrape')
    def scrape_product(self, request):
        """
        POST endpoint: Scrape Amazon product from URL
        
        Request body:
        {
            "url": "https://www.amazon.com/dp/BXXXXXXXXXX"
        }
        
        Returns: Product details or error message
        """
        serializer = ScrapeProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        url = serializer.validated_data['url']

        # Scrape the product
        scraped_data = scrape_amazon_product(url)

        if 'error' in scraped_data:
            return Response(
                {'error': scraped_data['error']},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if product already exists
        try:
            product = AmazonProduct.objects.get(asin=scraped_data['asin'])
            # Update existing product
            from decimal import Decimal
            product.current_price = Decimal(str(scraped_data['current_price']))
            product.original_price = Decimal(str(scraped_data['original_price'])) if scraped_data.get('original_price') else None
            product.rating = scraped_data.get('rating')
            product.number_of_reviews = scraped_data.get('number_of_reviews', 0)
            product.availability = scraped_data.get('availability', 'Unknown')
            product.image_url = scraped_data.get('image_url')
            product.save()
            return Response(
                AmazonProductSerializer(product).data,
                status=status.HTTP_200_OK
            )
        except AmazonProduct.DoesNotExist:
            # Create new product
            from decimal import Decimal
            product_data = {
                'url': url,
                'asin': scraped_data['asin'],
                'title': scraped_data['title'],
                'current_price': Decimal(str(scraped_data['current_price'])),
                'original_price': Decimal(str(scraped_data['original_price'])) if scraped_data.get('original_price') else None,
                'currency': scraped_data.get('currency', 'USD'),
                'rating': scraped_data.get('rating'),
                'number_of_reviews': scraped_data.get('number_of_reviews', 0),
                'image_url': scraped_data.get('image_url'),
                'availability': scraped_data.get('availability', 'Unknown'),
            }
            product = AmazonProduct.objects.create(**product_data)
            return Response(
                AmazonProductSerializer(product).data,
                status=status.HTTP_201_CREATED
            )


class PriceTrackerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing price trackers.
    
    Endpoints:
    - GET /api/trackers/ - List all price trackers
    - POST /api/trackers/ - Create a new price tracker
    - GET /api/trackers/{id}/ - Get tracker details
    - PATCH /api/trackers/{id}/ - Update tracker
    - DELETE /api/trackers/{id}/ - Delete tracker
    - POST /api/trackers/check-prices/ - Check all active trackers for price drops
    """
    queryset = PriceTracker.objects.all()
    serializer_class = PriceTrackerSerializer
    permission_classes = [AllowAny]
    filterset_fields = ['product_id', 'user_email', 'status']

    def create(self, request, *args, **kwargs):
        """
        Create a new price tracker
        
        Request body:
        {
            "product_id": 1,
            "user_email": "user@example.com",
            "target_price": 25.50
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # Send confirmation email to the user who created the tracker
        try:
            tracker = serializer.instance
            product = tracker.product
            send_tracker_confirmation_email(tracker.user_email, product, tracker.target_price)
        except Exception:
            # Do not fail creation if email sending fails
            pass

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['post'], url_path='check-prices')
    def check_prices(self, request):
        """
        Check all active price trackers and send emails if price drops
        """
        active_trackers = PriceTracker.objects.filter(
            status='active',
            email_sent=False
        )

        results = []
        for tracker in active_trackers:
            product = tracker.product
            
            # Refresh product data (price, availability) before checking
            try:
                refreshed = scrape_amazon_product(product.url)
                if 'error' not in refreshed and refreshed.get('asin'):
                    from decimal import Decimal
                    # update fields if present
                    product.current_price = Decimal(str(refreshed.get('current_price', product.current_price)))
                    if refreshed.get('original_price'):
                        product.original_price = Decimal(str(refreshed.get('original_price')))
                    product.availability = refreshed.get('availability', product.availability)
                    product.rating = refreshed.get('rating', product.rating)
                    product.number_of_reviews = refreshed.get('number_of_reviews', product.number_of_reviews)
                    product.image_url = refreshed.get('image_url', product.image_url)
                    product.save()
            except Exception:
                # If refresh fails, continue with stored values
                pass

            # Check if current price is at or below target price
            if product.current_price <= tracker.target_price:
                # Send email
                email_sent = send_price_alert_email(tracker.user_email, product)
                
                if email_sent:
                    tracker.status = 'triggered'
                    tracker.email_sent = True
                    tracker.triggered_at = timezone.now()
                    tracker.save()
                    
                    results.append({
                        'tracker_id': tracker.id,
                        'product': product.title,
                        'email': tracker.user_email,
                        'message': 'Email sent successfully',
                        'status': 'success'
                    })

        return Response({
            'total_checked': active_trackers.count(),
            'emails_sent': len(results),
            'results': results
        }, status=status.HTTP_200_OK)


# ===== Frontend Views (Jinja Templates) =====

from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from decimal import Decimal
from django.utils import timezone


def home(request):
    """Render homepage with URL input form"""
    return render(request, 'Scraping_Event/home.html')


@require_http_methods(["POST"])
@csrf_protect
def scrape_product_view(request):
    """Handle product scraping from URL input"""
    url = request.POST.get('url', '').strip()
    
    if not url:
        return render(request, 'Scraping_Event/home.html', {
            'error': 'Please enter a valid Amazon product URL'
        })
    
    # Validate URL
    if 'amazon.' not in url.lower():
        return render(request, 'Scraping_Event/home.html', {
            'error': 'Please enter a valid Amazon product URL (must contain amazon.)'
        })
    
    # Scrape the product
    scraped_data = scrape_amazon_product(url)
    
    if 'error' in scraped_data:
        return render(request, 'Scraping_Event/home.html', {
            'error': scraped_data['error']
        })
    
    # Check if product already exists
    try:
        product = AmazonProduct.objects.get(asin=scraped_data['asin'])
        # Update existing product
        product.current_price = Decimal(str(scraped_data['current_price']))
        product.original_price = Decimal(str(scraped_data['original_price'])) if scraped_data.get('original_price') else None
        product.rating = scraped_data.get('rating')
        product.number_of_reviews = scraped_data.get('number_of_reviews', 0)
        product.availability = scraped_data.get('availability', 'Unknown')
        product.image_url = scraped_data.get('image_url')
        product.save()
    except AmazonProduct.DoesNotExist:
        # Create new product
        product = AmazonProduct.objects.create(
            url=url,
            asin=scraped_data['asin'],
            title=scraped_data['title'],
            current_price=Decimal(str(scraped_data['current_price'])),
            original_price=Decimal(str(scraped_data['original_price'])) if scraped_data.get('original_price') else None,
            currency=scraped_data.get('currency', 'USD'),
            rating=scraped_data.get('rating'),
            number_of_reviews=scraped_data.get('number_of_reviews', 0),
            image_url=scraped_data.get('image_url'),
            availability=scraped_data.get('availability', 'Unknown'),
        )
    
    # Redirect to product details page
    return redirect('product_detail', pk=product.id)


def product_detail(request, pk):
    """Display product details and price tracker form"""
    try:
        product = AmazonProduct.objects.get(pk=pk)
    except AmazonProduct.DoesNotExist:
        return render(request, 'Scraping_Event/product_detail.html', {
            'error': 'Product not found'
        })
    
    context = {
        'product': product,
        'tracker_success': request.GET.get('tracker_success'),
        'tracker_error': request.GET.get('tracker_error'),
    }
    
    return render(request, 'Scraping_Event/product_detail.html', context)


@require_http_methods(["POST"])
@csrf_protect
def create_tracker_view(request):
    """Handle price tracker creation from form submission"""
    product_id = request.POST.get('product_id')
    email = request.POST.get('email', '').strip()
    target_price = request.POST.get('target_price', '').strip()
    
    try:
        product = AmazonProduct.objects.get(id=product_id)
    except AmazonProduct.DoesNotExist:
        return render(request, 'Scraping_Event/product_detail.html', {
            'error': 'Product not found',
            'product': None
        })
    
    # Validate email
    if not email or '@' not in email:
        return redirect(f'/product/{product_id}/?tracker_error=Invalid+email+address')
    
    # Validate target price
    try:
        target_price_decimal = Decimal(target_price)
        if target_price_decimal <= 0:
            return redirect(f'/product/{product_id}/?tracker_error=Target+price+must+be+greater+than+0')
        if target_price_decimal > product.current_price:
            return redirect(f'/product/{product_id}/?tracker_error=Target+price+must+be+less+than+or+equal+to+current+price')
    except:
        return redirect(f'/product/{product_id}/?tracker_error=Invalid+target+price')
    
    # Check if tracker already exists
    existing = PriceTracker.objects.filter(
        product=product,
        user_email=email,
        target_price=target_price_decimal
    ).first()
    
    if existing:
        return redirect(f'/product/{product_id}/?tracker_error=You+already+have+a+tracker+for+this+price')
    
    # Create tracker
    try:
        tracker = PriceTracker.objects.create(
            product=product,
            user_email=email,
            target_price=target_price_decimal,
            status='active',
            email_sent=False
        )
        # Send confirmation email for frontend-created trackers
        try:
            send_tracker_confirmation_email(email, product, target_price_decimal)
        except Exception:
            pass
        return redirect(f'/product/{product_id}/?tracker_success=Price+alert+created+successfully')
    except Exception as e:
        return redirect(f'/product/{product_id}/?tracker_error=Error+creating+tracker')
