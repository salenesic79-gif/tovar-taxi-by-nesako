from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('signup/sender/', views.signup_sender_view, name='signup_sender'),
    path('signup/carrier/', views.signup_carrier_view, name='signup_carrier'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('create-shipment/', views.create_shipment, name='create_shipment'),
    path('freight-exchange/', views.freight_exchange, name='freight_exchange'),
    path('shipment/<int:pk>/', views.shipment_detail, name='shipment_detail'),
    path('shipment/<int:pk>/offer/', views.make_offer_view, name='make_offer'),
    path('vehicles/', views.manage_vehicles, name='manage_vehicles'),
    path('settings/', views.settings_view, name='settings'),
    
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    
    # Vehicle API endpoints
    path('vehicle/<int:vehicle_id>/', views.vehicle_detail_api, name='vehicle_detail_api'),
    path('vehicle/add/', views.vehicle_add_api, name='vehicle_add_api'),
    path('vehicle/<int:vehicle_id>/edit/', views.vehicle_edit_api, name='vehicle_edit_api'),
    path('vehicle/<int:vehicle_id>/toggle/', views.vehicle_toggle_api, name='vehicle_toggle_api'),
    path('vehicle/<int:vehicle_id>/delete/', views.vehicle_delete_api, name='vehicle_delete_api'),
]
