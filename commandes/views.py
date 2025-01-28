from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework import status
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Produit, Sandwich, Commande
from .serializers import ProduitSerializer, SandwichSerializer, CommandeSerializer

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
