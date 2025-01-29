import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import commandes.routing  # Import du fichier contenant les routes WebSocket

# Assurer que Django est bien initialisé
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fablab_api.settings')
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(commandes.routing.websocket_urlpatterns)
    ),
})