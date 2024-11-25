from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView
)

from .views import (
    UserViewSet,
    AddressViewSet,
    PhysicalAddressViewSet,
    CreditCardViewSet,
    LoginView,
    CustomLogoutView,
    OTPViewSet, 
    ChatViewSet,
    MessageViewSet,
    AllChatsViewSet,

)

# Initialize the router
router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('addresses', AddressViewSet, basename='address')
router.register('physical-addresses', PhysicalAddressViewSet, basename='physicaladdress')
router.register('credit-cards', CreditCardViewSet, basename='creditcard')
router.register(r'chats', ChatViewSet, basename='chat')
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'all-chats', AllChatsViewSet, basename='all_chats')


# Define urlpatterns with JWT token routes and router URLs
urlpatterns = [
    # JWT Token management paths
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # User authentication paths
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),

    # OTP paths
    path('otp/', OTPViewSet.as_view({'post': 'generate_otp'}), name='generate_otp'),
    path('otp/verify/', OTPViewSet.as_view({'post': 'verify_otp'}), name='verify_otp'),

    # Include the router URLs
    path('', include(router.urls)),
]
