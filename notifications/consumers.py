import json

from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        # Ensure the user is authenticated
        # if self.user.is_anonymous:
        #     await self.close()
        #     return

        self.group_name = f"user_{1}"

        # Add the user to their group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Send a welcome message upon connection
        await self.send(text_data=json.dumps({
            "title": "Connected",
            "message": "WebSocket connection established successfully!",
        }))

    async def disconnect(self, close_code):
        """Remove user from group on disconnect"""
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_notification(self, event):
        """Send a notification message to the user"""
        await self.send(text_data=json.dumps({
            "title": event["title"],
            "message": event["message"],
        }))
