from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from common_bases.base_models import BaseModel
from .managers import AccountManager


# Create your models here.
class Account(AbstractUser):

    username = None
    email = models.EmailField(_('email address'), unique=True)
    avatar = models.ImageField(upload_to='avatars', null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = AccountManager()


class EmailUpdateRequest(BaseModel):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    new_email = models.EmailField(null=True, blank=True)

    def __str__(self):
        return self.user.first_name


class PasswordReset(BaseModel):
    email = models.EmailField()
    secretkey = models.CharField(null=True)
    token = models.CharField()

    def __str__(self):
        return self.email
