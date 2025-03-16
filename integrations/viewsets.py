from rest_framework import status
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response

from common_bases.permissions import IsAdminOrHasPermission
from common_bases.viewsets import InitialModelViewSet
from integrations.models import IntegrationAccess
from integrations.serializers import IntegrationAccessSerializer


class IntegrationsViewSet(InitialModelViewSet):
    queryset = IntegrationAccess.objects.all()

    def get_permissions(self):
        self.permission_classes = [IsAdminOrHasPermission]
        return super(self.__class__, self).get_permissions()

    def get_serializer_class(self):
        return IntegrationAccessSerializer

    @extend_schema(
        request=None,
        responses={
            200: IntegrationAccessSerializer(many=True),
        },
        operation_id='integration_list',
        tags=['Integration'],
    )
    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
