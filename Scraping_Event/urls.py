from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AmazonProductViewSet, PriceTrackerViewSet

router = DefaultRouter()
router.register(r'products', AmazonProductViewSet, basename='product')
router.register(r'trackers', PriceTrackerViewSet, basename='tracker')

urlpatterns = [
    path('', include(router.urls)),
]
