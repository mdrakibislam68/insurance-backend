from django.conf import settings
from django.apps import apps
from django.contrib.auth import get_user_model

DefaultUser = get_user_model()
Account = apps.get_model(settings.AUTH_USER_MODEL, require_ready=False) if hasattr(settings, 'AUTH_USER_MODEL') else DefaultUser
