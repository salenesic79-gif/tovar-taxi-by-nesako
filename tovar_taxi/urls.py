from django.contrib import admin
from django.urls import path
from tovar_taxi import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.pocetna_strana, name='pocetna_strana'),
    path('tovar/', views.lista_tovara, name='lista_tovara'),
    path('tovar/<int:tovar_id>/', views.detalji_tovara, name='detalji_tovara'),
]
