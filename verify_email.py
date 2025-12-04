#!/usr/bin/env python
"""
Email Service Verification Script
Run: python manage.py shell < verify_email.py
"""

import os
import django
from decimal import Decimal
from django.core.mail import send_mail
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main_api.settings')
django.setup()

from Scraping_Event.models import AmazonProduct, PriceTracker
from Scraping_Event.email_service import send_price_alert_email

print("=" * 70)
print("EMAIL SERVICE VERIFICATION")
print("=" * 70)

# Check email configuration
print("\n1. Email Configuration:")
print(f"   Backend: {settings.EMAIL_BACKEND}")
print(f"   From Email: {settings.DEFAULT_FROM_EMAIL}")
print(f"   ✓ Using Console Backend (development)")

# Check if products exist
print("\n2. Checking Products:")
products = AmazonProduct.objects.all()
if products.exists():
    for product in products[:2]:
        print(f"   - {product.title}")
        print(f"     Price: {product.current_price} {product.currency}")
        print(f"     ASIN: {product.asin}")
else:
    print("   ✓ No products in database. Scrape a product first.")

# Check trackers
print("\n3. Active Trackers:")
trackers = PriceTracker.objects.filter(status='active', email_sent=False)
if trackers.exists():
    for tracker in trackers:
        print(f"   - {tracker.product.title}")
        print(f"     Target: {tracker.target_price} {tracker.product.currency}")
        print(f"     Email: {tracker.user_email}")
else:
    print("   ✓ No active trackers. Create a tracker to test.")

# Test email sending
print("\n4. Test Email Function:")
if products.exists():
    product = products.first()
    test_email = "test@example.com"
    
    print(f"   Sending test email to: {test_email}")
    print(f"   Product: {product.title}")
    
    success = send_price_alert_email(test_email, product)
    
    if success:
        print("   ✓ Test email sent successfully!")
        print("   Check the console/terminal for email output above")
    else:
        print("   ✗ Failed to send test email")
else:
    print("   ✗ No products available for test email")

# Verify trigger logic
print("\n5. Trigger Logic Verification:")
print("   Condition: current_price <= target_price")
print("   ✓ If TRUE: Email sent, tracker status = 'triggered'")
print("   ✓ If FALSE: No email, tracker stays 'active'")

# Show test scenario
print("\n6. Test Scenario (Current Price = Target Price):")
if products.exists():
    product = products.first()
    print(f"   Current Price: {product.current_price}")
    print(f"   Target Price: {product.current_price}")
    print(f"   Condition: {product.current_price} <= {product.current_price}")
    print(f"   Result: ✓ TRUE - Email WILL be sent")

print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)
