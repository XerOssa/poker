import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
import poker_app.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'poker_app.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                poker_app.routing.websocket_urlpatterns
            )
        )
    ),
})