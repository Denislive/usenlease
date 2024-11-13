from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet,
    TagViewSet,
    EquipmentViewSet,
    ImageViewSet,
    SpecificationViewSet,
    ReviewViewSet,
    CartViewSet,
    OrderViewSet,
    OrderItemViewSet,
    CartItemViewSet,
    RootCategoryListView
)

# Create a router and register the viewsets
router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('tags', TagViewSet, basename='tag')
router.register('equipments', EquipmentViewSet, basename='equipment')
router.register('images', ImageViewSet, basename='image')
router.register('specifications', SpecificationViewSet, basename='specification')
router.register('reviews', ReviewViewSet, basename='review')
router.register('cart-items', CartItemViewSet, basename='cart-item')
router.register('cart', CartViewSet, basename='cart')

router.register('orders', OrderViewSet, basename='order')
router.register('order-items', OrderItemViewSet, basename='order-item')

urlpatterns = [
    path('', include(router.urls)),  # Include all the registered routes
    path('root-categories/', RootCategoryListView.as_view(), name='root-category-list'),

]