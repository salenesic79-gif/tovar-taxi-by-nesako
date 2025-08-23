from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('signup/sender/', views.signup_sender_view, name='signup_sender'),
    path('signup/carrier/', views.signup_carrier_view, name='signup_carrier'),
]
