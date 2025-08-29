from django.urls import path
from django.contrib.auth import views as auth_views
from . import views, api_views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('signup/', views.signup_view, name='signup'),
    path('signup/sender/', views.signup_sender, name='signup_sender'),
    path('signup/carrier/', views.signup_carrier, name='signup_carrier'),
    path('create-shipment/', views.create_shipment, name='create_shipment'),
    path('freight-exchange/', views.freight_exchange, name='freight_exchange'),
    path('shipment/<int:pk>/', views.shipment_detail_view, name='shipment_detail'),
    path('make-offer/<int:shipment_id>/', views.make_offer, name='make_offer'),
    path('vehicles/', views.manage_vehicles, name='manage_vehicles'),
    path('settings/', views.settings_view, name='settings'),
    path('terms/', views.terms_and_conditions, name='terms'),
    
    # Ture i Chat
    path('ture/', views.ture_list, name='ture_list'),
    path('ture/<int:tura_id>/', views.tura_detail, name='tura_detail'),
    path('chat/<int:tura_id>/', views.chat_view, name='chat_view'),
    path('notifikacije/', views.notifikacije_view, name='notifikacije'),
    
    # API endpoints - Vozila
    path('api/vehicles/', views.get_vehicles, name='api_vehicles'),
    path('api/vehicles/create/', views.create_vehicle_api, name='api_create_vehicle'),
    path('api/vehicles/<int:vehicle_id>/update/', views.update_vehicle_api, name='api_update_vehicle'),
    path('api/vehicles/<int:vehicle_id>/delete/', views.delete_vehicle_api, name='api_delete_vehicle'),
    path('api/vehicles/<int:vehicle_id>/toggle-status/', views.toggle_vehicle_status, name='api_toggle_vehicle_status'),
    
    # API endpoints - Ture
    path('api/ture/kreiraj/', api_views.kreiraj_turu, name='api_kreiraj_turu'),
    path('api/ture/<int:tura_id>/potvrdi/', api_views.potvrdi_turu, name='api_potvrdi_turu'),
    path('api/ture/<int:tura_id>/odbij/', api_views.odbij_turu, name='api_odbij_turu'),
    path('api/ture/<int:tura_id>/preuzeto/', api_views.potvrdi_preuzimanje, name='api_potvrdi_preuzimanje'),
    path('api/ture/<int:tura_id>/isporuceno/', api_views.potvrdi_isporuku, name='api_potvrdi_isporuku'),
    
    # API endpoints - Chat
    path('api/chat/<int:tura_id>/poruke/', api_views.get_chat_poruke, name='api_get_chat_poruke'),
    path('api/chat/<int:tura_id>/posalji/', api_views.posalji_poruku, name='api_posalji_poruku'),
    
    # API endpoints - Notifikacije
    path('api/notifikacije/', api_views.get_notifikacije, name='api_get_notifikacije'),
    path('api/notifikacije/<int:notif_id>/procitano/', api_views.oznaci_notifikaciju_procitanu, name='api_oznaci_procitano'),
    
    # API endpoints - Plaćanja
    path('api/transakcije/rezervisi/', api_views.rezervisi_sredstva, name='api_rezervisi_sredstva'),
    
    # WebSocket test
    path('websocket-test/', views.websocket_test, name='websocket_test'),
    
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', views.LogoutView.as_view(next_page='home'), name='logout'),
]
