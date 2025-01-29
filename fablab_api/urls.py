from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from commandes.views import (
    ProduitViewSet, 
    SandwichViewSet, 
    CommandeViewSet, 
    stock_actuel,
    TemperatureViewSet,
    verifier_poids_commande,
    ScanViewSet # 🔹 Ajout de l'import pour la vérification du poids
)


from django.conf import settings
from django.conf.urls.static import static

# Création du routeur pour les ViewSets
router = DefaultRouter()
router.register(r'produits', ProduitViewSet)
router.register(r'sandwiches', SandwichViewSet)
router.register(r'commandes', CommandeViewSet)
router.register(r'temperature', TemperatureViewSet)  # Ajout de la route pour la température
router.register(r'scans', ScanViewSet)  # Ajout de la route pour Scan

# Définition des URL du projet
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),  # Inclut toutes les routes API
    path('api/stock/', stock_actuel, name='stock'),  # Ajout de l'endpoint pour le stock
    path('api/verification-poids/', verifier_poids_commande, name="verification-poids"),  # 🔹 Nouveau endpoint pour la vérification du poids
]

# Ajoute cette ligne pour servir les fichiers statiques en mode DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
