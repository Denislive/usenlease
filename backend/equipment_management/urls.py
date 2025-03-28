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
    RootCategoryListView,
    OrderActionView,
    CreateCheckoutSessionView,
    SessionStatusView,
    UserEquipmentView,
    UserEditableEquipmentView,
)
from user_management.views import ReportViewSet, ContactViewSet, CompanyInfoView, FAQViewSet


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
router.register('reports', ReportViewSet, basename='report')
router.register('contact', ContactViewSet, basename='contact')
router.register('orders', OrderViewSet, basename='order')
router.register('order-items', OrderItemViewSet, basename='order-item')
router.register('faqs', FAQViewSet, basename='faq')


urlpatterns = [
    # Include all the registered routes from the router
    path('', include(router.urls)),

    # Checkout and session status
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create_checkout_session'),
    path('session-status/', SessionStatusView.as_view(), name='session_status'),

    # Order actions
    path('orders/<str:pk>/<str:action>/', OrderActionView.as_view(), name='order-action'),
    path('order-items/<str:pk>/total-booked/', OrderItemViewSet.as_view({'get': 'list_booked_items'}), name='total-booked'),
    path('order-items/<str:pk>/approve/', OrderItemViewSet.as_view({'post': 'approve'}), name='approve'),

    # Custom order actions (initiate_pickup, confirm_pickup, confirm_return)
    path('order-items/<str:pk>/initiate_pickup/', OrderViewSet.as_view({'post': 'initiate_pickup'}), name='initiate-pickup'),
    path('order-items/<str:pk>/confirm_pickup/', OrderViewSet.as_view({'post': 'confirm_pickup'}), name='confirm-pickup'),
    path('order-items/<str:pk>/confirm_return/', OrderViewSet.as_view({'post': 'confirm_return'}), name='confirm-return'),

    # Root categories and user equipment
    path('root-categories/', RootCategoryListView.as_view(), name='root-category-list'),
    path('user-equipment/', UserEquipmentView.as_view(), name='user-equipment'),
    path('user-editable-equipment/', UserEditableEquipmentView.as_view(), name='user-editable-equipment-list'),
    path('equipments/<str:pk>/related/', EquipmentViewSet.as_view({'get': 'related'}), name='related-items'),


    # Company info
    path('company-info/', CompanyInfoView.as_view(), name='company-info'),
]