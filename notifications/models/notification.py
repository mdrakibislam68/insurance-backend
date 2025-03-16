from django.db import models

from ..models.base import AbstractNotification


class Notification(AbstractNotification):
    """Concrete Notification Model"""
    CHANNELS = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('websocket', 'WebSocket'),
        ('push', 'Push'),
    ]

    channel = models.CharField(max_length=20, choices=CHANNELS, default='email')

    def send(self):
        from ..services.manager import NotificationService
        NotificationService.notify(self.user, self.title, self.message, [self.channel])
