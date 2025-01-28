from django.urls import path
from .consumers import StockConsumer

websocket_urlpatterns = [
    path('ws/stock/', StockConsumer.as_asgi()),  # Route WebSocket pour le stock
]
