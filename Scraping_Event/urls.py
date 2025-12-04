from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AmazonProductViewSet, 
    PriceTrackerViewSet,
    home,
    scrape_product_view,
    product_detail,
    create_tracker_view
)

router = DefaultRouter()
router.register(r'products', AmazonProductViewSet, basename='product')
router.register(r'trackers', PriceTrackerViewSet, basename='tracker')

urlpatterns = [
    # Frontend routes
    path('', home, name='home'),
    path('scrape/', scrape_product_view, name='scrape_product'),
    path('product/<int:pk>/', product_detail, name='product_detail'),
    path('tracker/create/', create_tracker_view, name='create_tracker'),
    
    # API routes
    path('api/', include(router.urls)),
]
