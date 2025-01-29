from django.contrib import admin
from .models import Produit, Sandwich, Commande, Temperature, Addstock  # N'oublie pas d'ajouter ConditionsMeteo

# Enregistre les modèles dans l'admin
admin.site.register(Produit)
admin.site.register(Sandwich)
admin.site.register(Commande)
admin.site.register(Temperature)  
admin.site.register(Addstock)  
