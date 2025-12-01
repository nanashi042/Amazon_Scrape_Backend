from rest_framework import serializers
from .models import AmazonProduct, PriceTracker


class AmazonProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = AmazonProduct
        fields = [
            'id', 'url', 'asin', 'title', 'current_price', 'original_price',
            'currency', 'rating', 'number_of_reviews', 'image_url',
            'description', 'availability', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'asin', 'created_at', 'updated_at']


class PriceTrackerSerializer(serializers.ModelSerializer):
    product = AmazonProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = PriceTracker
        fields = [
            'id', 'product', 'product_id', 'user_email', 'target_price',
            'status', 'email_sent', 'created_at', 'triggered_at'
        ]
        read_only_fields = ['id', 'status', 'email_sent', 'created_at', 'triggered_at']

    def create(self, validated_data):
        product_id = validated_data.pop('product_id')
        try:
            product = AmazonProduct.objects.get(id=product_id)
        except AmazonProduct.DoesNotExist:
            raise serializers.ValidationError({"product_id": "Product not found."})

        validated_data['product'] = product
        return super().create(validated_data)


class ScrapeProductSerializer(serializers.Serializer):
    """Serializer for scraping product from URL"""
    url = serializers.URLField()

    def validate_url(self, value):
        if 'amazon.' not in value:
            raise serializers.ValidationError("Please provide a valid Amazon product URL.")
        return value
