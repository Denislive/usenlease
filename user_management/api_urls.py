from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from .api_views import (
    UserViewSet,
    AddressViewSet,
    PhysicalAddressViewSet,
    CreditCardViewSet
)

# Initialize the router
router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('addresses', AddressViewSet, basename='address')
router.register('physical-addresses', PhysicalAddressViewSet, basename='physicaladdress')
router.register('credit-cards', CreditCardViewSet, basename='creditcard')

# Define urlpatterns with JWT token routes and router URLs
urlpatterns = [
    path('', include(router.urls)),
    # JWT Token management paths
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
