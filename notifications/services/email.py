from django.core.mail import send_mail
from ..services.base import BaseNotificationService

class EmailNotificationService(BaseNotificationService):
    """Handles Email Notifications"""

    def send(self):
        send_mail(
            self.title,
            self.message,
            self.from_email,
            [self.user.email],
            fail_silently=False,
        )
