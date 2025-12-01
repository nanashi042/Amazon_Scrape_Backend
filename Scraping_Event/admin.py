from django.contrib import admin
from .models import AmazonProduct, PriceTracker


@admin.register(AmazonProduct)
class AmazonProductAdmin(admin.ModelAdmin):
    list_display = ['asin', 'title', 'current_price', 'rating', 'created_at']
    list_filter = ['currency', 'created_at', 'updated_at']
    search_fields = ['asin', 'title']
    readonly_fields = ['asin', 'created_at', 'updated_at']


@admin.register(PriceTracker)
class PriceTrackerAdmin(admin.ModelAdmin):
    list_display = ['product', 'user_email', 'target_price', 'status', 'email_sent', 'created_at']
    list_filter = ['status', 'email_sent', 'created_at']
    search_fields = ['user_email', 'product__title', 'product__asin']
    readonly_fields = ['created_at', 'triggered_at']
