from django.db import models
import uuid  # Pour générer un code-barres unique

class Produit(models.Model):
    TAILLE_CHOICES = [
        ("M", "Moyen"),
        ("L", "Large"),
        ("XL", "Extra Large"),
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


class Sandwich(models.Model):
    TAILLE_CHOICES = [
        ("M", "Moyen"),
        ("L", "Large"),
        ("XL", "Extra Large"),
    ]

    nom = models.CharField(max_length=100, unique=True)  # Nom du sandwich
    taille = models.CharField(max_length=10, choices=TAILLE_CHOICES)  # Taille du sandwich
    produits = models.ManyToManyField(Produit)  # Produits qui composent le sandwich
    poids_total = models.FloatField(default=0, help_text="Poids total du sandwich en grammes")  # Poids total du sandwich

    def save(self, *args, **kwargs):
        """ Vérifie si le sandwich est nouveau avant de l'ajouter en base """
        is_new = self.pk is None  

        """ Sauvegarde initiale pour générer un ID si nécessaire """
        super().save(*args, **kwargs)  

        """ Ajoute les produits compatibles seulement si le sandwich est nouveau """
        if is_new:
            produits_compatibles = Produit.objects.filter(taille=self.taille)
            self.produits.set(produits_compatibles)  # Ajoute les produits compatibles

        """ Recalcule le poids total du sandwich """
        total_poids = sum(produit.poids for produit in self.produits.all())
        self.poids_total = total_poids

        """ Sauvegarde finale avec le poids total mis à jour """
        super().save(update_fields=["poids_total"])

    def __str__(self):
        return f"{self.nom} ({self.taille}) - {self.poids_total}g"


class Commande(models.Model):
    STATUS_CHOICES = [
        ("en attente", "En attente"),
        ("validée", "Validée"),
    ]

    sandwich = models.ForeignKey(Sandwich, on_delete=models.CASCADE)  # Lien vers un sandwich commandé
    quantite = models.PositiveIntegerField(default=1)  # Quantité commandée
    poids_total = models.FloatField(default=0, help_text="Poids total de la commande en grammes")  # Poids total
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="en attente")  # Statut de la commande
    code_barre = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)  # Code-barres unique

    def save(self, *args, **kwargs):
        """ Calcule automatiquement le poids total de la commande avant de sauvegarder. """
        if self.sandwich:
            self.poids_total = self.sandwich.poids_total * self.quantite
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Commande {self.id} - {self.sandwich.nom} x {self.quantite} - {self.poids_total}g - {self.status}"
