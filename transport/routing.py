from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/location/(?P<tour_id>\w+)/$', consumers.LocationConsumer.as_asgi()),
    re_path(r'ws/notifications/(?P<user_id>\w+)/$', consumers.NotificationConsumer.as_asgi()),
    re_path(r'ws/chat/(?P<tour_id>\w+)/$', consumers.ChatConsumer.as_asgi()),
]
