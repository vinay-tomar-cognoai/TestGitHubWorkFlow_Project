from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/cobrowse/(?P<room_name>[a-zA-Z0-9-_]+)/(?P<sender>\w+)/$', consumers.CobrowsingConsumer.as_asgi()),
]
