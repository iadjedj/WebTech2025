import json
from channels.generic.websocket import AsyncWebsocketConsumer

class StockConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """ Connexion WebSocket acceptée et ajout au groupe stock_updates """
        await self.channel_layer.group_add("stock_updates", self.channel_name)
        await self.accept()
        print("✅ WebSocket connecté et ajouté au groupe stock_updates")

    async def disconnect(self, close_code):
        """ Déconnexion WebSocket et suppression du groupe """
        await self.channel_layer.group_discard("stock_updates", self.channel_name)
        print("❌ WebSocket déconnecté")

    async def receive(self, text_data):
        """ Réception d'un message via WebSocket """
        data = json.loads(text_data)
        message = data.get("message", "")

        # Répondre au client WebSocket
        await self.send(text_data=json.dumps({
            "message": f"Message reçu : {message}"
        }))

    async def send_stock_update(self, event):
        """ Envoie une mise à jour du stock à tous les clients WebSocket """
        stock_data = event["data"]
        print(f"📡 WebSocket envoi : {stock_data}")  # Debugging
        await self.send(text_data=json.dumps(stock_data))
