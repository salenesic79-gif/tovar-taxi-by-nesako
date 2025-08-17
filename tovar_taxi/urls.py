path('', include('transport.urls'))
# tovar_taxi/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('transport.urls')),
]
