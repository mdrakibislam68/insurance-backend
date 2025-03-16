from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from common_bases.permissions import IsAdminOrHasPermission
from common_bases.serializers import EmptySerializer
from common_bases.viewsets import InitialModelViewSet
from .models import GeneralSettings
from .serializers import GeneralSettingsSerializer, AppGeneralSettingsSerializer, TestEmailSerializer
from .tasks import task_test_email


class GeneralSettingsViewSets(InitialModelViewSet):
    queryset = GeneralSettings.objects.all()
    required_permissions = []

    def get_permissions(self):
        if self.action == 'list':
            self.required_permissions = ['roles.api_read_settings']
            self.permission_classes = [IsAdminOrHasPermission]
        elif self.action in ['update', 'generate_webhook_secret']:
            self.required_permissions = ['roles.api_edit_settings']
            self.permission_classes = [IsAdminOrHasPermission]
        elif self.action in ['app_general_settings', 'test_email']:
            self.permission_classes = [AllowAny]
        return super(self.__class__, self).get_permissions()

    def get_serializer_class(self):
        if self.action == 'test_email':
            return TestEmailSerializer
        elif self.action == 'clean_cache':
            return EmptySerializer
        return GeneralSettingsSerializer

    @extend_schema(
        request=GeneralSettingsSerializer,
        responses={
            200: GeneralSettingsSerializer,
        },
        operation_id='general_settings_list',
        tags=['GeneralSettings'],
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=GeneralSettingsSerializer,
        responses={
            200: GeneralSettingsSerializer,
        },
        operation_id='update_general_settings',
        tags=['GeneralSettings'],
    )
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_instance = serializer.save()
        serializer = self.get_serializer(updated_instance)
        return Response(serializer.data)

    @extend_schema(
        request=None,
        responses={
            200: AppGeneralSettingsSerializer,
        },
        operation_id='app_general_settings',
        tags=['GeneralSettings'],
    )
    @action(detail=False, methods=['GET'], url_path='app-general-settings')
    def app_general_settings(self, request):
        queryset = self.get_queryset().first()
        serializer = AppGeneralSettingsSerializer(queryset)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='test-email')
    def test_email(self, request, *args, **kwargs):
        serializer = TestEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.data['send_type'] == 'direct':
            send_mail(
                'Subject here',
                'Here is the message.',
                settings.DEFAULT_FROM_EMAIL,
                [serializer.data['email']],
            )
        else:
            task_test_email.delay(serializer.data['email'])
        return Response("Email test")

    @action(detail=False, methods=['post'], url_path='clean-cache')
    def clean_cache(self, request):
        cache.clear()
        return Response("Cache cleared")
