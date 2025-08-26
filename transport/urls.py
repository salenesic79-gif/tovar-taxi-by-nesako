from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('signup/sender/', views.signup_sender_view, name='signup_sender'),
    path('signup/carrier/', views.signup_carrier_view, name='signup_carrier'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('create-shipment/', views.create_shipment_view, name='create_shipment'),
    path('freight-exchange/', views.freight_exchange_view, name='freight_exchange'),
    path('shipment/<int:pk>/', views.shipment_detail_view, name='shipment_detail'),
    path('shipment/<int:pk>/offer/', views.make_offer_view, name='make_offer'),
    path('vehicles/', views.manage_vehicles_view, name='manage_vehicles'),
    path('settings/', views.settings_view, name='settings'),
]
