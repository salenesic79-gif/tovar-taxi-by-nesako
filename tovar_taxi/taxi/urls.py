from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('taxi_app.urls')),  # vodi sve na tvoju aplikaciju taxi_app
]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # početna stranica
]
