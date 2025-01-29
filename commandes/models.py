from django.db import models
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

class Produit(models.Model):
    """ Modèle représentant un produit individuel """
    
    TAILLE_CHOICES = [
        ("S", "Petit"),
        ("M", "Moyen"),
        ("L", "Large"),
    ]
    
    COULEUR_CHOICES = [
        ("Jaune", "Jaune"),
        ("Rouge", "Rouge"),
        ("Vert", "Vert"),
        ("Bleu", "Bleu"),
    ]

    nom = models.CharField(max_length=100)  # Nom du produit
    taille = models.CharField(max_length=10, choices=TAILLE_CHOICES)  # Taille du produit
    poids = models.FloatField(help_text="Poids en grammes")  # Poids unitaire du produit
    quantite_stock = models.PositiveIntegerField(default=0)  # Quantité en stock
    couleur = models.CharField(max_length=10, choices=COULEUR_CHOICES, default="Jaune")  # Couleur du produit

    def __str__(self):
        return f"{self.nom} ({self.taille}, {self.couleur}) - {self.poids}g - Stock: {self.quantite_stock}"

    @classmethod
    def get_stock_total(cls):
        """ Retourne la somme de tous les produits en stock """
        return cls.objects.aggregate(total_stock=models.Sum("quantite_stock"))["total_stock"] or 0

    def save(self, *args, **kwargs):
        """ 🔹 Sauvegarde et envoie une mise à jour du stock via WebSocket """
        super().save(*args, **kwargs)  # 🔹 Sauvegarde l'objet normalement

        # 🔹 Envoi de la mise à jour WebSocket pour le stock
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "stock_updates",
            {"type": "send_stock_update"}
        )


class Sandwich(models.Model):
    """ Modèle représentant un sandwich composé de plusieurs produits """
    
    TAILLE_CHOICES = [
        ("S", "Petit"),
        ("M", "Moyen"),
        ("L", "Large"),
    ]

    nom = models.CharField(max_length=100, unique=True)
    taille = models.CharField(max_length=10, choices=TAILLE_CHOICES)
    produits = models.ManyToManyField(Produit)  # Relation ManyToMany
    poids_total = models.FloatField(default=0)
    temps_cuisson = models.PositiveIntegerField(default=0, help_text="Temps de cuisson total du sandwich (secondes)")

    def save(self, *args, **kwargs):
        """ 🔹 Mise à jour automatique du poids total et du temps de cuisson """
        super().save(*args, **kwargs)  # 🔹 Sauvegarde l'objet pour générer l'ID

        if self.produits.exists():  # Vérifie si des produits sont associés
            self.poids_total = sum(produit.poids for produit in self.produits.all())
            self.temps_cuisson = max(produit.temps_cuisson for produit in self.produits.all())  # ⚠️ Prend le MAXIMUM du temps de cuisson
            super().save(update_fields=["poids_total", "temps_cuisson"])  # 🔹 Sauvegarde finale après mise à jour

    def __str__(self):
        return f"{self.nom} ({self.taille}) - {self.poids_total}g - Cuisson: {self.temps_cuisson}s"


class Commande(models.Model):
    """ Modèle représentant une commande d'un ou plusieurs sandwiches """
    
    STATUS_CHOICES = [
        ("en attente", "En attente"),
        ("ticket imprimé", "Ticket imprimé"),
        ("validée", "Validée"),
        ("en cuisson", "En cuisson"),
        ("terminée", "Terminée"),
    ]

    sandwich = models.ForeignKey(Sandwich, on_delete=models.CASCADE)  # Lien vers un sandwich commandé
    quantite = models.PositiveIntegerField(default=1)  # Quantité commandée
    poids_total = models.FloatField(default=0, help_text="Poids total de la commande en grammes")  # Poids total
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="en attente")  # Statut de la commande
    date_commande = models.DateTimeField(auto_now_add=True)  # Date de création de la commande

    def save(self, *args, **kwargs):
        """ 🔹 Calcule automatiquement le poids total de la commande avant de sauvegarder. """
        if self.sandwich:
            self.poids_total = self.sandwich.poids_total * self.quantite

        super().save(*args, **kwargs)

        """ 🔹 Mise à jour du stock des produits si la commande est terminée """
        if self.status == "terminée":
            for produit in self.sandwich.produits.all():
                produit.quantite_stock -= self.quantite
                produit.save()

    def __str__(self):
        return f"Commande {self.id} - {self.sandwich.nom} x {self.quantite} - {self.poids_total}g - {self.status}"
