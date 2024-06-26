
import os
import poker_app.routing
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.routing import get_default_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'poker_app.settings')




application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            poker_app.routing.websocket_urlpatterns
        )
    ),
})

