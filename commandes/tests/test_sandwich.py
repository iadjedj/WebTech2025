from django.test import TestCase
from commandes.models import Produit

class ProduitTestCase(TestCase):
    def test_creation_produit(self):
        """ Vérifie si un produit peut être créé correctement """
        produit = Produit.objects.create(
            nom="Pain Burger",
            taille="M",
            poids=50.0,
            quantite_stock=10,
            couleur="Jaune",
            temps_cuisson=5
        )
        
        # Vérifie que le produit a bien été enregistré
        self.assertEqual(produit.nom, "Pain Burger")
        self.assertEqual(produit.taille, "M")
        self.assertEqual(produit.poids, 50.0)
        self.assertEqual(produit.quantite_stock, 10)
        self.assertEqual(produit.couleur, "Jaune")
        self.assertEqual(produit.temps_cuisson, 5)
