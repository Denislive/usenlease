from django.urls import path
from . import views 


urlpatterns = [
    path('latest-equipments/', views.LatestEquipmentList.as_view()),
    path('', views.home, name='home'),
    path('about/', views.about_us, name='about'),
    path('services/', views.services, name='services'),
    path('service-detail/', views.service_detail, name='service_detail'),
    path('search/', views.search_view, name='search'),
    path('equipments/', views.equipment_list, name='equipments'),
    path('equipments/<slug:slug>/<int:id>/', views.equipment_detail, name='equipment_detail'),


    # path('equipment/details/', views.equipment_detail, name='equipment_detail'),

    # path('profile/', views.profile, name='profile'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),


    path('equipment/create/', views.equipment_create_view, name='equipment-create'),

    path('add-to-cart/<slug:slug>/<int:id>/', views.add_to_cart, name='add-to-cart'),
    path('add-single-item-to-cart/<slug:slug>/<int:id>/', views.add_single_item_to_cart, name='add-single-item-to-cart'),
    path('remove-from-cart/<slug:slug>/<int:id>/', views.remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug:slug>/<int:id>/', views.remove_single_item_from_cart, name='remove-single-item-from-cart'),


    # path('add_equipment/', views.add_equipment, name='equip'),
    path('contact/', views.contact_us, name='contact'),
    path('stripe/', views.stripe_view, name='stripe'),

    path('paypal/', views.paypal_view, name='paypal'),


    # path('cart/', views.CartSummaryView.as_view(), name='cart'),
    # path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('success/', views.successMsg, name='success'),

    path('create-payment/', views.create_payment, name='create-payment'),

    # path('equipment/<int:equipment_id>/review/', views.submit_equipment_review, name='submit_equipment_review'),
    # path('owner/<int:owner_id>/review/', views.submit_owner_review, name='submit_owner_review'),

]
