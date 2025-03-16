from django.conf import settings

from ..services.email import EmailNotificationService
from ..services.websocket import WebSocketNotificationService


class NotificationService:
    """Centralized Notification Manager"""

    DEFAULT_SERVICES = {
        "email": EmailNotificationService,
        "websocket": WebSocketNotificationService,
    }

    @staticmethod
    def get_services():
        """Allows users to extend notification services dynamically"""
        custom_services = getattr(settings, "CUSTOM_NOTIFICATION_SERVICES", {})
        return {**NotificationService.DEFAULT_SERVICES, **custom_services}

    @staticmethod
    def notify(user, title, message, channels=["email"], **kwargs):
        services = NotificationService.get_services()
        for channel in channels:
            service_class = services.get(channel)
            if service_class:
                service_class(user, title, message, **kwargs).send()
