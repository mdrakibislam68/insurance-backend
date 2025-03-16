# Create your views here.
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import CustomGroup
from .permissions import IsAdminOrHasPermission
from .serializers import GroupSerializer, PermissionSerializer, PermissionGroupSerializer, SetUserPermissionsSerializer, \
    RoleUsersSerializer, RoleOptionListSerializer, UserPermissionsSerializer, UserDeleteSerializer
from .services.permission_service import PermissionService

Account = get_user_model()


class RolesViewSet(viewsets.ModelViewSet):
    queryset = CustomGroup.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAdminOrHasPermission]
    required_permissions = ['roles.view_customgroup']

    def get_serializer_class(self):
        if self.action == 'role_users':
            return RoleUsersSerializer
        elif self.action == 'role_options':
            return RoleOptionListSerializer
        elif self.action == 'delete_user':
            return UserDeleteSerializer
        return GroupSerializer

    @extend_schema(
        request=None,
        responses={
            200: None,
        },
        operation_id='delete_role',
        tags=['Roles'],
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_default:
            raise ValidationError({'detail': f'Cannot delete default role: {instance.name}'})
        self.perform_destroy(instance)
        message = f'{instance.name} role is deleted successfully!'
        return Response({'message': message})

    @extend_schema(
        request=None,
        responses={
            200: RoleUsersSerializer,
        },
        operation_id='role_users',
        tags=['Roles'],
    )
    @action(detail=True, methods=['GET'], name='Role Users', url_path='role-users')
    def role_users(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @extend_schema(
        request=None,
        responses={200: RoleOptionListSerializer},
        operation_id='role_options',
        tags=['Roles'],
    )
    @action(detail=False, methods=['GET'], name='Role Options', url_path='role-options')
    def role_options(self, request):
        queryset = CustomGroup.objects.all().exclude(name__in=['Admin', 'Super Admin'])
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=UserDeleteSerializer,
        responses={200: None},
        operation_id='delete_user',
        tags=['Roles'],
    )
    @action(detail=False, methods=['POST'], name='Delete User', url_path='delete-user')
    def delete_user(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = get_object_or_404(Account, email=email)
        user.delete()
        return Response({'message': 'User deleted successfully'})


class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAdminOrHasPermission]

    def get_serializer_class(self):
        if self.action == 'set_user_permissions':
            return SetUserPermissionsSerializer
        if self.action == 'permission_list':
            return PermissionGroupSerializer
        return PermissionSerializer

    @extend_schema(
        request=None,
        responses={
            200: PermissionGroupSerializer,
        },
        operation_id='permission_list',
        tags=['Permissions'],
    )
    @action(detail=False, methods=['GET'], name='Permission List', url_path='permission-list')
    def permission_list(self, request):
        permission_service = PermissionService()
        permissions = permission_service.get_permissions()
        serializer = PermissionGroupSerializer(permissions, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=SetUserPermissionsSerializer,
        responses={
            200: None,
        },
        operation_id='set_user_permissions',
        tags=['Permissions'],
    )
    @action(detail=False, methods=['POST'], name='Set User Permission', url_path='set-user-permissions')
    def set_user_permissions(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Permissions added successfully'})

    @extend_schema(
        responses={200: UserPermissionsSerializer},
        operation_id='user_permissions',
        tags=['Roles'],
        parameters=[
            OpenApiParameter(
                name='email',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Email of the user to fetch permissions for',
                required=True
            ),
        ]
    )
    @action(detail=False, methods=['GET'], name='User Permissions', url_path='user-permissions')
    def user_permissions(self, request):
        email = request.query_params.get('email')
        if not email:
            raise ValidationError({'non_field_errors': ['Email is required in query parameter']})
        user = get_object_or_404(Account, email=email)
        individual_permissions = user.user_permissions.all()
        individual_permissions_ids = list(individual_permissions.values_list('id', flat=True))

        data = {
            'email': user.email,
            'permissions': individual_permissions_ids,
        }
        serializer = UserPermissionsSerializer(data)
        return Response(serializer.data)
