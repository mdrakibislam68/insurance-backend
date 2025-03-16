from django.conf import settings
from django.utils.module_loading import import_string
from user_management.serializers import DefaultSignUpSerializer, DefaultProfileInfoSerializer

SignUpSerializer = import_string(settings.AUTH_SIGNUP_SERIALIZER) if hasattr(settings, 'AUTH_SIGNUP_SERIALIZER') else DefaultSignUpSerializer
ProfileInfoSerializer = import_string(settings.AUTH_PROFILEINFO_SERIALIZER) if hasattr(settings, 'AUTH_PROFILEINFO_SERIALIZER') else DefaultProfileInfoSerializer