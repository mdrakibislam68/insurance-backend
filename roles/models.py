from django.contrib.auth.models import Group
from django.db import models


class CustomGroup(Group):
    description = models.TextField(blank=True, null=True)
    is_default = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
