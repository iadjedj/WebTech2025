import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import commandes.routing  # Import du fichier contenant les routes WebSocket

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fablab_api.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(commandes.routing.websocket_urlpatterns)
    ),
})
