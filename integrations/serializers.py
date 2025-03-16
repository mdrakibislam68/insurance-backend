from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import IntegrationAccess

Account = get_user_model()


class IntegrationAccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegrationAccess
        fields = '__all__'
