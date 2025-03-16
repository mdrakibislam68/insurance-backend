from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from ..services.base import BaseNotificationService


class WebSocketNotificationService(BaseNotificationService):
    """Handles Real-time WebSocket Notifications"""

    def send(self):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{self.user.id}",
            {
                "type": "send_notification",
                "title": self.title,
                "message": self.message,
            },
        )
