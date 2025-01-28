

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from commandes.views import ProduitViewSet, SandwichViewSet, CommandeViewSet, stock_actuel  # Assure-toi que l'import est correct

# Création du routeur pour les ViewSets
router = DefaultRouter()
router.register(r'produits', ProduitViewSet)
router.register(r'sandwiches', SandwichViewSet)
router.register(r'commandes', CommandeViewSet)

# Définition des URL du projet
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),  # Inclut toutes les routes API
    path('api/stock/', stock_actuel, name='stock'),  # Ajout de l'endpoint pour le stock
]
