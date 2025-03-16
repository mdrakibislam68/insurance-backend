from abc import ABC, abstractmethod


class BaseNotificationService(ABC):
    """Abstract Base Class for Notification Services"""

    def __init__(self, user, title, message, **kwargs):
        self.user = user
        self.title = title
        self.message = message

    @abstractmethod
    def send(self):
        """To be implemented by subclasses"""
        pass
