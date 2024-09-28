from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    # User URLs
    path('user/create/', views.create_user_view, name='create_user'),
    path('user/update/<int:pk>/', views.update_user_view, name='update_user'),
    
    path('user/login/', views.user_login_view, name='login'),
    path('logout/', views.user_logout, name='logout'),

    path('user/profile/', views.profile, name='profile'),

    # Address URLs
    path('address/create/', views.create_address_view, name='create_address'),
    path('address/update/<int:pk>/', views.update_address_view, name='update_address'),

    # Physical Address URLs
    path('physical-address/create/', views.create_physical_address_view, name='create_physical_address'),
    path('physical-address/update/', views.update_physical_address_view, name='update_physical_address'),


    # Credit Card URLs
    path('credit-card/create/', views.create_credit_card_view, name='create_credit_card'),
    path('credit-card/update/', views.update_credit_card_view, name='update_credit_card'),

     # Delete Address URL
    path('address/delete/<int:pk>/', views.delete_address_view, name='delete_address'),

    # Delete Credit Card URL
    path('credit-card/delete/<int:pk>/', views.delete_credit_card_view, name='delete_credit_card'),
]
