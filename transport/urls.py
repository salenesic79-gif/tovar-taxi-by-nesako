from django.urls import path
from . import views

app_name = 'transport'

urlpatterns = [
    # Home page
    path('', views.home_view, name='transport_home'),
    
    
    # Authentication
    path('login/', views.custom_login_view, name='custom_login'),
    path('signup/sender/new/', views.signup_sender_new_view, name='signup_sender_new'),
    path('signup/carrier/new/', views.signup_carrier_new_view, name='signup_carrier_new'),
    
    # Post-registration workflows
    path('create-shipment-request/', views.create_shipment_request, name='create_shipment_request'),
    path('create-route-availability/', views.create_route_availability, name='create_route_availability'),
    
    # B2B and Instant Delivery
    path('instant-delivery/', views.create_instant_delivery, name='create_instant_delivery'),
    path('food-delivery/', views.create_food_delivery, name='create_food_delivery'),
    path('premium-subscription/', views.premium_subscription_view, name='premium_subscription'),
    
    # Driver extended functionality
    path('driver-dashboard-extended/', views.driver_dashboard_extended, name='driver_dashboard_extended'),
    path('accept-delivery/<int:delivery_id>/', views.accept_delivery, name='accept_delivery'),
    path('update-delivery-status/<int:delivery_id>/', views.update_delivery_status, name='update_delivery_status'),
    path('update-location/', views.update_location, name='update_location'),
    
    # Dashboards
    path('shipper-dashboard/', views.shipper_dashboard, name='shipper_dashboard'),
    path('carrier-dashboard/', views.carrier_dashboard, name='carrier_dashboard'),
    
    # Shipments
    path('create-shipment/', views.create_shipment, name='create_shipment'),
    path('shipment/<int:pk>/', views.shipment_detail, name='shipment_detail'),
    path('freight-exchange/', views.freight_exchange, name='freight_exchange'),
    
    # Offers
    path('make-offer/<int:shipment_id>/', views.make_offer, name='make_offer'),
    
    # Vehicles
    path('manage-vehicles/', views.manage_vehicles, name='manage_vehicles'),
    path('add-vehicle/', views.add_vehicle, name='add_vehicle'),
    path('vehicle/<int:vehicle_id>/', views.vehicle_details, name='vehicle_details'),
    path('edit-vehicle/<int:vehicle_id>/', views.edit_vehicle, name='edit_vehicle'),
    
    # Tours
    path('my-tours/', views.my_tours, name='my_tours'),
    path('tour/<int:pk>/', views.tour_detail, name='tour_detail'),
    path('create-tour/', views.create_tour, name='create_tour'),
    path('update-tour-location/', views.update_tour_location, name='update_tour_location'),
    
    # Cargo and Payment System (NEW)
    path('cargo-map/', views.cargo_map_view, name='cargo_map'),
    path('create-cargo/', views.create_cargo_view, name='create_cargo'),
    path('calculate-price/', views.calculate_price_view, name='calculate_price'),
    path('cargo-list/', views.cargo_list_view, name='cargo_list'),
    path('cargo/<int:cargo_id>/', views.cargo_detail_view, name='cargo_detail'),
    path('accept-cargo/<int:cargo_id>/', views.accept_cargo_view, name='accept_cargo'),
    path('cargo/<int:cargo_id>/start-transport/', views.start_transport_view, name='start_transport'),
    path('confirm-delivery/<int:cargo_id>/', views.confirm_delivery_view, name='confirm_delivery'),
    
    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    
    # API endpoints
    path('api/accept-offer/<int:offer_id>/', views.accept_offer_api, name='accept_offer_api'),
    path('api/send-message/<int:tour_id>/', views.send_message_api, name='send_message_api'),
    path('api/notifications/', views.notifications_api, name='notifications_api'),
    path('api/notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('api/notifications/<int:notification_id>/action/', views.notification_action, name='notification_action'),
    
    # Stripe Payments
    path('stripe-webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('stripe-cancel-subscription/', views.stripe_cancel_subscription, name='stripe_cancel_subscription'),
    
    # WebSocket test
    path('websocket-test/', views.websocket_test, name='websocket_test'),
    
    # PWA URLs
    path('pwa-manifest/', views.pwa_manifest, name='pwa_manifest'),
    path('manifest.json', views.pwa_manifest, name='pwa_manifest'),
    path('sw.js', views.service_worker, name='service_worker'),
]
