from django.db import models
from common_bases.base_models import BaseModel


# Create your models here.
class IntegrationAccess(BaseModel):
    PROVIDER_LIST = (
        ('ruuvi', 'Ruuvi'),
    )
    name = models.CharField(max_length=255, blank=False, null=False)
    email = models.EmailField(max_length=255, blank=False, null=False)
    refresh_token = models.CharField(max_length=255, blank=True, null=True)
    access_token = models.CharField(max_length=255, blank=True, null=True)
    provider = models.CharField(max_length=255, choices=PROVIDER_LIST, default='ruuvi', null=True)

    def __str__(self):
        return self.name
