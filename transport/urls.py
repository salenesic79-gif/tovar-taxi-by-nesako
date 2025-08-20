from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.user_signup, name='signup'),
    path('order/create/', views.order_create, name='order_create'),
    path('vehicle/create/', views.vehicle_create, name='vehicle_create'),
]
