from rest_framework import serializers
from .models import Produit, Sandwich, Commande

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
    sandwich = serializers.PrimaryKeyRelatedField(queryset=Sandwich.objects.all())

    class Meta:
        model = Commande
        fields = '__all__'
