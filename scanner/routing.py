from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/scans/(?P<scan_id>\d+)/status/$', consumers.ScanStatusConsumer.as_asgi()),
]
