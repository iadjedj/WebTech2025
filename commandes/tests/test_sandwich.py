from django.test import TestCase
from commandes.models import Produit, Sandwich


class SandwichTestCase(TestCase):
    def setUp(self):
        self.produit1 = Produit.objects.create(nom="Tomate", taille="M", poids=50)
        self.produit2 = Produit.objects.create(nom="Fromage", taille="M", poids=100)
        self.sandwich = Sandwich.objects.create(nom="Sandwich Test", taille="M")
        self.sandwich.produits.add(self.produit1, self.produit2)
    
    def test_poids_total(self):
        """ Vérifie que le poids total du sandwich est bien calculé """
        self.sandwich.save()
        self.assertEqual(self.sandwich.poids_total, 150)
