# transport/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='transport/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('create-order/', views.create_order, name='create_order'),
    path('orders/', views.order_list, name='order_list'),
    path('accept-order/<int:order_id>/', views.accept_order, name='accept_order'),
    # Privremeni URL za detalje narudžbine
    path('order/<int:order_id>/', views.order_list, name='order_details'),
]
