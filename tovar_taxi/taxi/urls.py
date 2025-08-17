from django.contrib import admin
from django.urls import path
from tovar import views  # Pretpostavljam da je ime vaše aplikacije 'tovar'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('tovar/', views.lista_tovara, name='lista_tovara'),
    path('tovar/<int:tovar_id>/', views.detalji_tovara, name='detalji_tovara'),
]
