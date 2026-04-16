# consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class EmployerStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if user.is_authenticated and user.role == "employer":
            self.group_name = f"employer_{user.id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_verification_status(self, event):
        # Send message to frontend
        await self.send(text_data=json.dumps({
            "verified": event["verified"]
        }))