from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework import status
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from .models import Produit, Sandwich, Commande, Temperature, Addstock
from .serializers import ProduitSerializer, SandwichSerializer, CommandeSerializer, TemperatureSerializer, AddstockSerializer

class ProduitViewSet(viewsets.ModelViewSet):
    """ API pour gérer les produits """
    queryset = Produit.objects.all()
    serializer_class = ProduitSerializer

class SandwichViewSet(viewsets.ModelViewSet):
    """ API pour gérer les sandwiches """
    queryset = Sandwich.objects.all()
    serializer_class = SandwichSerializer

class CommandeViewSet(viewsets.ModelViewSet):
    """ API pour gérer les commandes """
    queryset = Commande.objects.all()
    serializer_class = CommandeSerializer

    @action(detail=True, methods=['post'])
    def changer_statut(self, request, pk=None):
        """ Permet de changer le statut d'une commande """
        commande = self.get_object()
        nouveau_statut = request.data.get("statut")

        if nouveau_statut not in dict(Commande.STATUS_CHOICES):
            return Response({"error": "Statut invalide"}, status=status.HTTP_400_BAD_REQUEST)

        commande.status = nouveau_statut
        commande.save()

        print(f"🛠️ Statut de la commande {commande.id} changé en {commande.status}")

        # Envoyer une mise à jour WebSocket après le changement de statut
        update_stock()

        return Response({"message": f"Statut changé en {commande.status}"}, status=status.HTTP_200_OK)

@api_view(['GET'])
def stock_actuel(request):
    """ Endpoint pour récupérer le stock des ingrédients """
    produits = Produit.objects.all()
    serializer = ProduitSerializer(produits, many=True)
    return Response(serializer.data)

def update_stock():
    """ Envoie une mise à jour du stock via WebSockets """
    channel_layer = get_channel_layer()
    
    if channel_layer is None:
        print("❌ ERREUR : `get_channel_layer()` est None. Vérifie que Django Channels est bien configuré.")
        return

    print("✅ `get_channel_layer()` fonctionne bien ! Envoi de la mise à jour du stock...")

    produits = Produit.objects.all()
    stock_data = [{"nom": p.nom, "quantite": p.quantite_stock} for p in produits]

    try:
        async_to_sync(channel_layer.group_send)(
            "stock_updates",
            {"type": "send_stock_update", "data": stock_data}
        )
        print("📡 WebSocket : mise à jour envoyée avec succès !")
    except Exception as e:
        print(f"❌ ERREUR WebSocket : {e}")

from rest_framework.decorators import api_view
from .models import Temperature
from .serializers import TemperatureSerializer

class TemperatureViewSet(viewsets.ModelViewSet):
    queryset = Temperature.objects.all()
    serializer_class = TemperatureSerializer

@csrf_exempt
def verifier_poids_commande(request):
    """ Vérifie si le poids mesuré correspond à la commande et met à jour son statut """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            code_commande = data.get("code_commande")
            poids_mesure = data.get("poids_mesure")

            # Vérifier que les champs existent
            if not code_commande or poids_mesure is None:
                return JsonResponse({"error": "Données manquantes"}, status=400)

            # Recherche de la commande
            commande = Commande.objects.filter(id=code_commande).first()

            if not commande:
                return JsonResponse({"error": "Commande non trouvée"}, status=404)

            # Vérification du poids avec une tolérance de ±5g
            tolerance = 5  
            if abs(commande.poids_total - poids_mesure) <= tolerance:
                commande.status = "terminée"
                message = "✅ Poids validé, commande terminée."
            else:
                commande.status = "en attente"  
                message = "❌ Erreur de poids, la commande repasse en attente."

            commande.save()

            return JsonResponse({"message": message, "status": commande.status})

        except json.JSONDecodeError:
            return JsonResponse({"error": "Format JSON invalide"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)

from rest_framework import viewsets
from .models import Addstock
from .serializers import AddstockSerializer
from rest_framework.decorators import action
from channels.layers import get_channel_layer

class AddstockViewSet(viewsets.ModelViewSet):
    """ API pour gérer l'ajout de stock """
    queryset = Addstock.objects.all()
    serializer_class = AddstockSerializer

    @action(detail=False, methods=['post'])
    def ajouter_stock(self, request):
        """ Ajoute du stock à un produit existant ou crée un nouveau produit si nécessaire """
        nom_produit = request.data.get("nom")
        taille_produit = request.data.get("taille")
        couleur_produit = request.data.get("couleur")
        quantite_a_ajouter = request.data.get("quantite_stock")
        poids_produit = request.data.get("poids")

        if not nom_produit or not quantite_a_ajouter or not poids_produit:
            return Response({"error": "Données manquantes"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            produit, created = Produit.objects.get_or_create(
                nom=nom_produit,
                taille=taille_produit,
                couleur=couleur_produit,
                defaults={"poids": poids_produit, "quantite_stock": quantite_a_ajouter}
            )

            if not created:
                produit.quantite_stock += int(quantite_a_ajouter)
                produit.save()

            # Envoyer une mise à jour WebSocket
            self.update_stock_via_websocket()

            message = f"✅ {quantite_a_ajouter} unités de {nom_produit} ajoutées au stock."
            return Response({"message": message}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update_stock_via_websocket(self):
        """ Envoie une mise à jour du stock via WebSockets """
        channel_layer = get_channel_layer()

        if channel_layer is None:
            print("❌ ERREUR : `get_channel_layer()` est None. Vérifie que Django Channels est bien configuré.")
            return

        produits = Produit.objects.all()
        stock_data = [{"nom": p.nom, "quantite": p.quantite_stock} for p in produits]

        try:
            async_to_sync(channel_layer.group_send)(
                "stock_updates",
                {"type": "send_stock_update", "data": stock_data}
            )
            print("📡 WebSocket : mise à jour envoyée avec succès !")
        except Exception as e:
            print(f"❌ ERREUR WebSocket : {e}")
