from rest_framework import serializers
from .models import Produit, Sandwich, Commande, Addstock, Temperature

class ProduitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produit
        fields = '__all__'  # Inclut tous les champs du modèle

class SandwichSerializer(serializers.ModelSerializer):
    produits = ProduitSerializer(many=True, read_only=True)  # 🔥 Retourne les produits sous forme d’objets
    produits_ids = serializers.PrimaryKeyRelatedField(
        queryset=Produit.objects.all(),
        many=True,
        write_only=True  # 🔥 Permet d'ajouter des produits via leur ID en POST
    )

    class Meta:
        model = Sandwich
        fields = '__all__'

    def create(self, validated_data):
        """ 🔹 Permet d'ajouter un sandwich avec ses produits """
        produits_data = validated_data.pop('produits_ids', [])  # Récupérer les produits sélectionnés (IDs)
        sandwich = Sandwich.objects.create(**validated_data)  # Créer le sandwich
        sandwich.produits.set(produits_data)  # Associer les produits
        return sandwich

    def update(self, instance, validated_data):
        """ 🔹 Permet de modifier un sandwich avec ses produits """
        produits_data = validated_data.pop('produits_ids', None)  # Récupérer les produits sélectionnés (IDs)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)  # Mettre à jour les autres champs

        if produits_data is not None:
            instance.produits.set(produits_data)  # Mettre à jour les produits liés

        instance.save()
        return instance

class CommandeSerializer(serializers.ModelSerializer):
    sandwich = SandwichSerializer(read_only=True)  # 🔥 Affiche l'objet sandwich en GET
    sandwich_id = serializers.PrimaryKeyRelatedField(
        queryset=Sandwich.objects.all(),
        write_only=True  # 🔥 Permet d'envoyer un ID en POST
    )

    class Meta:
        model = Commande
        fields = '__all__'

    def create(self, validated_data):
        """ 🔹 Permet de créer une commande avec un ID de sandwich """
        sandwich = validated_data.pop('sandwich_id')  # Récupérer l'ID du sandwich
        commande = Commande.objects.create(sandwich=sandwich, **validated_data)  # Associer le sandwich
        return commande

class TemperatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Temperature
        fields = ['date_heure', 'temperature', 'humidite']  # Utilise 'date_heure' au lieu de 'created_at'

class AddstockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Addstock
        fields = ['id', 'nom', 'taille', 'quantite_stock']

    def create(self, validated_data):
        """ 🔹 Ajoute du stock à un produit existant ou crée un nouveau produit """
        produit, created = Produit.objects.get_or_create(
            nom=validated_data["nom"],
            taille=validated_data.get("taille", "M"),  # Par défaut, taille moyenne
            defaults={"quantite_stock": 0}  # Initialise la quantité à 0
        )

        # 🔹 Met à jour le stock
        produit.quantite_stock += validated_data["quantite_stock"]
        produit.save()
        
        return produit
