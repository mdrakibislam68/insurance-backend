from drf_spectacular.utils import extend_schema
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.response import Response
from rest_framework import status


class InitialModelViewSet(ModelViewSet):
    @extend_schema(exclude=True)
    def list(self, request):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(exclude=True)
    def create(self, request):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(exclude=True)
    def retrieve(self, request, pk=None):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(exclude=True)
    def update(self, request, pk=None):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(exclude=True)
    def partial_update(self, request, pk=None):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(exclude=True)
    def destroy(self, request, pk=None):
        return Response(status=status.HTTP_400_BAD_REQUEST)


class InitialViewSet(ViewSet):
    @extend_schema(exclude=True)
    def list(self, request):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(exclude=True)
    def create(self, request):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(exclude=True)
    def retrieve(self, request, pk=None):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(exclude=True)
    def update(self, request, pk=None):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(exclude=True)
    def partial_update(self, request, pk=None):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(exclude=True)
    def destroy(self, request, pk=None):
        return Response(status=status.HTTP_400_BAD_REQUEST)