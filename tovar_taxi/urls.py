"""
URL configuration for tovar_taxi project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from transport.views import home_view, custom_logout_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('transport/', include('transport.urls', namespace='transport')),
    path('accounts/logout/', transport.views.custom_logout_view, name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
    # Override accounts/profile/ redirect
    path('accounts/profile/', home_view, name='profile_redirect'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
