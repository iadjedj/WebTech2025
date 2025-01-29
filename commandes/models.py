from django.db import models
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import m2m_changed, pre_save
from django.dispatch import receiver
from django.utils import timezone
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
    poids_total = models.FloatField(default=0)  # ✅ Poids total du sandwich

    def save(self, *args, **kwargs):
        """ 🔹 Mise à jour automatique du poids total """
        super().save(*args, **kwargs)  # 🔹 Sauvegarde l'objet pour générer l'ID

        if self.produits.exists():  # Vérifie si des produits sont associés
            self.poids_total = sum(produit.poids for produit in self.produits.all())  # ✅ Somme des poids des produits
            super().save(update_fields=["poids_total"])  # 🔹 Sauvegarde finale après mise à jour

    def __str__(self):
        return f"{self.nom} ({self.taille}) - {self.poids_total}g"


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
    poids_total = models.FloatField(default=0, help_text="Poids total de la commande en grammes")  # ✅ Poids total mis à jour
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="en attente")  # Statut de la commande
    date_commande = models.DateTimeField(auto_now_add=True)  # Date de création de la commande

    def save(self, *args, **kwargs):
        """ 🔹 Calcule automatiquement le poids total de la commande avant de sauvegarder. """
        if self.sandwich:
            self.poids_total = self.sandwich.poids_total * self.quantite  # ✅ Poids total basé sur la quantité

        super().save(*args, **kwargs)

        """ 🔹 Mise à jour du stock des produits si la commande est terminée """
        if self.status == "terminée":
            for produit in self.sandwich.produits.all():
                produit.quantite_stock -= self.quantite
                produit.save()

    def __str__(self):
        return f"Commande {self.id} - {self.sandwich.nom} x {self.quantite} - {self.poids_total}g - {self.status}"


@receiver(pre_save, sender=Commande)
def update_commande_poids(sender, instance, **kwargs):
    """ 🔹 Met à jour automatiquement le poids total de la commande avant de sauvegarder """
    if instance.sandwich:
        instance.poids_total = instance.sandwich.poids_total * instance.quantite
class ConditionsMeteo(models.Model):
    """ Modèle représentant les conditions météo à un moment donné """
    
    date_heure = models.DateTimeField(auto_now_add=True)  # Date et heure avec seconde de l'enregistrement
    temperature = models.FloatField(help_text="Température en degrés Celsius")  # Température en °C
    humidite = models.FloatField(help_text="Humidité en pourcentage")  # Humidité en %

    def __str__(self):
        return f"Conditions du {self.date_heure.strftime('%Y-%m-%d %H:%M:%S')} - Temp: {self.temperature}°C, Humidité: {self.humidite}%"

@receiver(pre_save, sender=Commande)
def update_stock_on_terminer(sender, instance, **kwargs):
    """ 🔹 Diminue le stock des produits lorsque la commande passe en statut 'terminée' """
    if instance.pk:  # Vérifier si la commande existe déjà (éviter sur création)
        ancienne_commande = Commande.objects.filter(pk=instance.pk).first()
        if ancienne_commande and ancienne_commande.status != "terminée" and instance.status == "terminée":
            for produit in instance.sandwich.produits.all():
                if produit.quantite_stock >= instance.quantite:
                    produit.quantite_stock -= instance.quantite
                    produit.save()
                else:
                    raise ValueError(f"Stock insuffisant pour {produit.nom} !")

class Temperature(models.Model):
    date_heure = models.DateTimeField(auto_now_add=True)
    temperature = models.FloatField(help_text="Température en degrés Celsius")
    humidite = models.FloatField(help_text="Humidité en pourcentage")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Conditions du {self.date_heure.strftime('%Y-%m-%d %H:%M:%S')} - Temp: {self.temperature}°C, Humidité: {self.humidite}%"

class Scan(models.Model):
    code = models.CharField(max_length=255, unique=True)
    poids = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Scan {self.code} - {self.poids} kg"