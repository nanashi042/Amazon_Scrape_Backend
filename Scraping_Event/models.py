from django.db import models
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import re

class AmazonProduct(models.Model):
    """Model to store Amazon product details"""
    url = models.URLField(unique=True)
    asin = models.CharField(max_length=20, unique=True, db_index=True)
    title = models.CharField(max_length=500)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=5, default='USD')
    rating = models.FloatField(null=True, blank=True)
    number_of_reviews = models.IntegerField(default=0)
    image_url = models.URLField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    availability = models.CharField(max_length=100, default='Unknown')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} - {self.current_price}"


class PriceTracker(models.Model):
    """Model to track price alerts for products"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('triggered', 'Triggered'),
    ]

    product = models.ForeignKey(AmazonProduct, on_delete=models.CASCADE, related_name='trackers')
    user_email = models.EmailField(db_index=True)
    target_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    email_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    triggered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('product', 'user_email', 'target_price')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.title} - Target: {self.target_price} for {self.user_email}"
