from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils import timezone
from django.db import IntegrityError
from .models import AmazonProduct, PriceTracker
from .serializers import AmazonProductSerializer, PriceTrackerSerializer, ScrapeProductSerializer
from .scraper import scrape_amazon_product
from .email_service import send_price_alert_email


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
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        except IntegrityError:
            return Response(
                {'error': 'A tracker with this product and email already exists.'},
                status=status.HTTP_400_BAD_REQUEST
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
