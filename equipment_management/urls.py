from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='index'),
    path('about-us/', views.about_us, name='about_us'),
    path('services/', views.services, name='services'),
    path('equipments/', views.equipment_list, name='equipment_list'),
    path('equipments/<int:pk>/', views.equipment_detail, name='equipment_detail'),
    path('contact-us/', views.contact_us, name='contact_us'),
]
