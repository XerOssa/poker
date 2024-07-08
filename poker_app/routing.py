from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/pokersocket/', consumers.PokerConsumer.as_asgi()),
]

