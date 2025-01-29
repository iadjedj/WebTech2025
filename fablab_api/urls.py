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
    AddstockViewSet  
)

from django.conf import settings
from django.conf.urls.static import static

# Création du routeur pour les ViewSets
router = DefaultRouter()
router.register(r'produits', ProduitViewSet)
router.register(r'sandwiches', SandwichViewSet)
router.register(r'commandes', CommandeViewSet)
router.register(r'temperature', TemperatureViewSet)  
router.register(r'addstock', AddstockViewSet, basename="addstock")  # ✅ Correction basename

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),  
    path('api/stock/', stock_actuel, name='stock'),  
    path('api/verification-poids/', verifier_poids_commande, name="verification-poids"),
    path('api/addstock/ajouter/', AddstockViewSet.as_view({'post': 'ajouter_stock'}), name='ajouter-stock'),  # ✅ Route POST
]

# Ajoute cette ligne pour servir les fichiers statiques en mode DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
