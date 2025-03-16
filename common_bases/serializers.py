from drf_spectacular.utils import extend_schema_serializer, OpenApiTypes
from rest_framework import serializers


class EmptySerializer(serializers.Serializer):
    pass


@extend_schema_serializer
class PaginatedResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.CharField(allow_null=True)
    previous = serializers.CharField(allow_null=True)
    results = serializers.ListField(child=serializers.Serializer())

    def __init__(self, *args, **kwargs):
        # Accept `child` argument for the results field
        child_serializer = kwargs.pop('child', None)
        super().__init__(*args, **kwargs)
        if child_serializer:
            self.fields['results'].child = child_serializer
