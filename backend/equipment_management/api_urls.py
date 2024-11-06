from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    CategoryViewSet,
    TagViewSet,
    EquipmentViewSet,
    ImageViewSet,
    SpecificationViewSet,
    ReviewViewSet,
    CartViewSet,
    OrderViewSet,
    OrderItemViewSet,
    CartItemViewSet
)

# Create a router and register the viewsets
router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'equipments', EquipmentViewSet, basename='equipment')
router.register(r'images', ImageViewSet, basename='image')
router.register(r'specifications', SpecificationViewSet, basename='specification')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'cart-items', CartItemViewSet, basename='cart-item')
router.register(r'cart', CartViewSet, basename='cart')

router.register(r'orders', OrderViewSet, basename='order')
router.register(r'order-items', OrderItemViewSet, basename='order-item')

urlpatterns = [
    path('', include(router.urls)),  # Include all the registered routes
]