import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
import scanner.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prowler_scanner.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            scanner.routing.websocket_urlpatterns
        )
    ),
})
