from django.db import models
from common_bases.base_models import BaseModel


# Create your models here.
class GeneralSettings(BaseModel):
    phone = models.JSONField(default=dict)
    setup_pages = models.JSONField(default=dict)
    company_logo = models.ImageField(upload_to='company_logo', null=True, blank=True)
    business_information = models.JSONField(default=dict)

    def __str__(self):
        return 'General Settings'
