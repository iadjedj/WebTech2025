import json
import django
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async

django.setup()

from .models import Produit

class StockConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """ Connexion WebSocket acceptée et ajout au groupe stock_updates """
        await self.channel_layer.group_add("stock_updates", self.channel_name)
        await self.accept()
        print("✅ WebSocket connecté et ajouté au groupe stock_updates")
        
        # 🔹 Envoi du stock total dès la connexion du client WebSocket
        await self.send_stock_update()

    async def disconnect(self, close_code):
        """ Déconnexion WebSocket et suppression du groupe """
        await self.channel_layer.group_discard("stock_updates", self.channel_name)
        print("❌ WebSocket déconnecté")

    async def receive(self, text_data):
        """ Réception d'un message via WebSocket (utilisable si on veut envoyer des commandes au serveur) """
        data = json.loads(text_data)
        message = data.get("message", "")

        # 🔹 Répondre au client WebSocket
        await self.send(text_data=json.dumps({
            "message": f"Message reçu : {message}"
        }))

    async def send_stock_update(self):
        """ 🔹 Envoie du stock total actuel aux clients WebSocket """
        stock_total = await sync_to_async(Produit.get_stock_total)()
        print(f"📡 Envoi du stock total via WebSocket : {stock_total} unités")
        await self.send(text_data=json.dumps({"stock_total": stock_total}))

    async def stock_update(self, event):
        """ 🔹 Réception d'une mise à jour et envoi aux clients WebSocket """
        stock_total = event["stock_total"]
        print(f"📡 Mise à jour WebSocket reçue : {stock_total} unités")
        await self.send(text_data=json.dumps({"stock_total": stock_total}))

    @staticmethod
    def broadcast_stock_update():
        """ 🔹 Envoi d'une mise à jour du stock via WebSocket à tous les clients connectés """
        channel_layer = get_channel_layer()
        stock_total = Produit.get_stock_total()
        async_to_sync(channel_layer.group_send)(
            "stock_updates",
            {
                "type": "stock_update",
                "stock_total": stock_total
            }
        )
