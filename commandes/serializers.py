from rest_framework import serializers
from .models import Produit, Sandwich, Commande, Temperature,Scan

class ProduitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produit
        fields = '__all__'  # Inclut tous les champs du modèle

class SandwichSerializer(serializers.ModelSerializer):
    produits = ProduitSerializer(many=True, read_only=True)  # Affiche les produits associés

    class Meta:
        model = Sandwich
        fields = '__all__'

class CommandeSerializer(serializers.ModelSerializer):
    sandwich = SandwichSerializer(read_only=True)  # Affiche le détail du sandwich

    class Meta:
        model = Commande
        fields = '__all__'

class TemperatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Temperature
        fields = ['date_heure', 'temperature', 'humidite']  # Utilise 'date_heure' au lieu de 'created_at'

class ScanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scan
        fields = '__all__'  # Ou ['id', 'code', 'poids'] si tu veux être plus précis
