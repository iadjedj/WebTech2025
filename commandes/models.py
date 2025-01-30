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

    nom = models.CharField(max_length=100, unique=True)  # ✅ Nom unique
    taille = models.CharField(max_length=10, choices=TAILLE_CHOICES)  
    poids = models.FloatField(help_text="Poids en grammes")  
    quantite_stock = models.PositiveIntegerField(default=0)  
    couleur = models.CharField(max_length=10, choices=COULEUR_CHOICES, default="Jaune")  

    def __str__(self):
        return f"{self.nom} ({self.taille}, {self.couleur}) - {self.poids}g - Stock: {self.quantite_stock}"

    @classmethod
    def get_stock_total(cls):
        """ Retourne la somme de tous les produits en stock """
        return cls.objects.aggregate(total_stock=models.Sum("quantite_stock"))["total_stock"] or 0

    def save(self, *args, **kwargs):
        """ 🔹 Sauvegarde et envoie une mise à jour du stock via WebSocket """
        super().save(*args, **kwargs)

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
    produits = models.ManyToManyField(Produit)  
    poids_total = models.FloatField(default=0)  

    def __str__(self):
        return f"{self.nom} ({self.taille}) - {self.poids_total}g"

@receiver(m2m_changed, sender=Sandwich.produits.through)
def update_sandwich_poids(sender, instance, **kwargs):
    """ 🔹 Met à jour le poids total du sandwich quand les produits changent """
    instance.poids_total = sum(produit.poids for produit in instance.produits.all())
    instance.save()

class Commande(models.Model):
    """ Modèle représentant une commande d'un ou plusieurs sandwiches """
    
    STATUS_CHOICES = [
        ("en attente", "En attente"),
        ("ticket imprimé", "Ticket imprimé"),
        ("validée", "Validée"),
        ("en cuisson", "En cuisson"),
        ("terminée", "Terminée"),
    ]

    sandwich = models.ForeignKey(Sandwich, on_delete=models.CASCADE)  
    quantite = models.PositiveIntegerField(default=1)  
    poids_total = models.FloatField(default=0, help_text="Poids total de la commande en grammes")  
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="en attente")  
    date_commande = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f"Commande {self.id} - {self.sandwich.nom} x {self.quantite} - {self.poids_total}g - {self.status}"

@receiver(pre_save, sender=Commande)
def update_commande_poids(sender, instance, **kwargs):
    """ 🔹 Met à jour automatiquement le poids total de la commande avant de sauvegarder """
    if instance.sandwich:
        instance.poids_total = instance.sandwich.poids_total * instance.quantite

@receiver(pre_save, sender=Commande)
def update_stock_on_terminer(sender, instance, **kwargs):
    """ 🔹 Diminue le stock des produits lorsque la commande passe en statut 'terminée' """
    if instance.pk:
        ancienne_commande = Commande.objects.filter(pk=instance.pk).first()
        if ancienne_commande and ancienne_commande.status != "terminée" and instance.status == "terminée":
            for produit in instance.sandwich.produits.all():
                produit.quantite_stock -= instance.quantite
                produit.save()

class Addstock(models.Model):
    nom = models.CharField(max_length=100)
    taille = models.CharField(max_length=10)
    quantite_stock = models.PositiveIntegerField(default=0)
    date_heure = models.DateTimeField(default=timezone.now)  # ✅ Ajout du default ici

    def __str__(self):
        return f"Stock ajouté le {self.date_heure.strftime('%Y-%m-%d %H:%M:%S')} - Quantité: {self.quantite_stock}"


class Temperature(models.Model):
    """ Modèle représentant la température enregistrée """
    
    date_heure = models.DateTimeField(auto_now_add=True)
    temperature = models.FloatField(help_text="Température en degrés Celsius")
    humidite = models.FloatField(help_text="Humidité en pourcentage")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Conditions du {self.date_heure.strftime('%Y-%m-%d %H:%M:%S')} - Temp: {self.temperature}°C, Humidité: {self.humidite}%"
