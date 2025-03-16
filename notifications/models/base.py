from uuid import uuid4

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class AbstractNotification(models.Model):
    """Abstract Base Class for Notifications"""
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def mark_as_read(self):
        self.is_read = True
        self.save()

    def send(self):
        """Override this method in subclasses to send notifications"""
        raise NotImplementedError("Subclasses must implement this method")
