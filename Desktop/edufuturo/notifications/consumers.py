import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Notification

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if not self.scope["user"].is_authenticated:
            await self.close()
            return

        self.user = self.scope["user"]
        self.group_name = f"user_{self.user.id}"

        # Entrar no grupo do usuário
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Recebe mensagem do grupo
    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            'id': event['id'],
            'verb': event['verb'],
            'actor': event['actor'],
            'timestamp': event['timestamp'],
            'read': event['read'],
            'type': event['notification_type'],
        })) 