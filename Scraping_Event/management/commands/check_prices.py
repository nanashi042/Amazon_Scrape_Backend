from django.core.management.base import BaseCommand
from django.utils import timezone
from Scraping_Event.models import PriceTracker, AmazonProduct
from Scraping_Event.scraper import scrape_amazon_product
from Scraping_Event.email_service import send_price_alert_email


class Command(BaseCommand):
    help = 'Check all active price trackers and send email alerts if prices drop'

    def handle(self, *args, **options):
        self.stdout.write('Starting price check...')
        
        active_trackers = PriceTracker.objects.filter(
            status='active',
            email_sent=False
        )

        self.stdout.write(f'Found {active_trackers.count()} active trackers to check')

        emails_sent = 0
        for tracker in active_trackers:
            product = tracker.product
            
            # Scrape latest price
            scraped_data = scrape_amazon_product(product.url)
            
            if 'error' not in scraped_data:
                # Update product price
                product.current_price = scraped_data['current_price']
                product.updated_at = timezone.now()
                product.save()
                
                # Check if price dropped to target
                if product.current_price <= tracker.target_price:
                    email_sent = send_price_alert_email(tracker.user_email, product)
                    
                    if email_sent:
                        tracker.status = 'triggered'
                        tracker.email_sent = True
                        tracker.triggered_at = timezone.now()
                        tracker.save()
                        emails_sent += 1
                        
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✓ Email sent to {tracker.user_email} for {product.title}'
                            )
                        )

        self.stdout.write(
            self.style.SUCCESS(f'Price check completed. {emails_sent} emails sent.')
        )
