"""
ASGI config for _core project — supports HTTP and WebSocket via Channels.
"""
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '_core.settings')

django_asgi_app = get_asgi_application()

from apps.notifications import routing as notification_routing

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter(
            notification_routing.websocket_urlpatterns
        )
    ),
})
