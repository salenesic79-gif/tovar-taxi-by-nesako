from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('signup/', views.signup_view, name='signup'),
    
    # Dashboards
    path('shipper-dashboard/', views.shipper_dashboard, name='shipper_dashboard'),
    path('carrier-dashboard/', views.carrier_dashboard, name='carrier_dashboard'),
    path('driver-dashboard/', views.driver_dashboard, name='driver_dashboard'),
    
    # Shipments
    path('create-shipment/', views.create_shipment, name='create_shipment'),
    path('shipment/<int:pk>/', views.shipment_detail, name='shipment_detail'),
    path('freight-exchange/', views.freight_exchange, name='freight_exchange'),
    
    # Offers
    path('make-offer/<int:shipment_id>/', views.make_offer, name='make_offer'),
    
    # Vehicles
    path('manage-vehicles/', views.manage_vehicles, name='manage_vehicles'),
    path('add-vehicle/', views.add_vehicle, name='add_vehicle'),
    
    # Tours
    path('my-tours/', views.my_tours, name='my_tours'),
    path('tour/<int:pk>/', views.tour_detail, name='tour_detail'),
    
    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    
    # API endpoints
    path('api/accept-offer/<int:offer_id>/', views.accept_offer_api, name='accept_offer_api'),
    path('api/send-message/<int:tour_id>/', views.send_message_api, name='send_message_api'),
    
    # WebSocket test
    path('websocket-test/', views.websocket_test, name='websocket_test'),
]
