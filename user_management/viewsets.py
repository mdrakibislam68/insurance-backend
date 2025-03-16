from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.decorators import action, parser_classes
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db.models import Q

from common_bases.permissions import IsAdminOrHasPermission
from .serializers import EmptySerializer, LoginSerializer, LoginResponseSerializer, CreateNewUserSerializer, \
    ResetPasswordSerializer, AccountActiveSerializer, ResetPasswordSendSerializer, ChangePasswordSerializer, \
    AccountActiveResponseSerializer, UserListSerializer, UserPermissionListSerializer, ResetCustomerPasswordSerializer, \
    UserSerializer, \
    GenerateTokenForCustomerSerializer, SearchUsersSerializer, AccountSerializer
from .services.auth_module_services import Account
from .services.auth_serializers_services import SignUpSerializer, ProfileInfoSerializer
from .services.auth_viewsets_services import send_signup_email, verify_user, login_user, send_reset_password_email, \
    reset_password, reset_customer_password, change_password, update_email, send_reset_password_secretkey, \
    login_customer
from .utils.viewsets import InitialModelViewSet


class AuthViewSets(InitialModelViewSet):
    queryset = []

    def get_serializer_class(self):
        if self.action == 'login':
            return LoginSerializer
        elif self.action == 'signup':
            return SignUpSerializer
        elif self.action in ['signup_verify', 'update_email']:
            return AccountActiveSerializer
        elif self.action == 'reset_password':
            return ResetPasswordSerializer
        elif self.action in ['reset_password_url_send', 'reset_password_secretkey_send']:
            return ResetPasswordSendSerializer
        elif self.action in ['get_profile_info', 'update_profile_info']:
            return ProfileInfoSerializer
        elif self.action == 'change_password':
            return ChangePasswordSerializer
        elif self.action in ['set_user_roles', 'users']:
            return UserListSerializer
        elif self.action == 'user_permissions':
            return UserPermissionListSerializer
        elif self.action == 'create_new_user':
            return CreateNewUserSerializer
        elif self.action == 'generate_token_for_customer':
            return GenerateTokenForCustomerSerializer
        elif self.action == 'search_users':
            return AccountSerializer
        return EmptySerializer

    def get_permissions(self):
        if self.action in ['login', 'login_customer', 'signup', 'signup_customer', 'signup_verify',
                           'reset_password_url_send', 'reset_password_secretkey_send', 'reset_password',
                           'reset_customer_password']:
            self.permission_classes = [AllowAny]
        elif self.action in ['set_user_roles', 'users', 'create_new_user', 'search_users']:
            self.permission_classes = [IsAdminOrHasPermission]
        elif self.action == 'generate_token_for_customer':
            self.permission_classes = [IsAdminUser]
        return super(self.__class__, self).get_permissions()

    @extend_schema(
        request=SignUpSerializer,
        responses={
            200: None,
        },
        operation_id='signup',
        tags=['Authentication'],
    )
    @action(detail=False, methods=['POST'], name='SignUp', url_path='signup')
    def signup(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        send_signup_email(user)
        return Response({'message': 'Your account has been successfully created!'})

    @extend_schema(
        request=AccountActiveSerializer,
        responses={
            200: AccountActiveResponseSerializer,
        },
        operation_id='signup_verify',
        tags=['Authentication'],
    )
    @action(detail=False, methods=['POST'], name='Account Active', url_path='signup-verify')
    def signup_verify(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        verified_data = verify_user(serializer.validated_data['uuid'])
        return Response(verified_data)

    @extend_schema(
        request=LoginSerializer,
        responses={
            200: LoginResponseSerializer,
        },
        operation_id='login',
        tags=['Authentication'],
    )
    @action(detail=False, methods=['POST'], name='Login', url_path='login')
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        login_data = login_user(serializer.validated_data['email'])
        return Response(login_data)

    @extend_schema(
        request=None,
        responses={
            200: ProfileInfoSerializer,
        },
        operation_id='get_profile_info',
        tags=['Authentication'],
    )
    @action(detail=False, methods=['GET'], name='Get Profile Info', url_path='get-profile-info')
    def get_profile_info(self, request):
        query = Account.objects.get(pk=request.user.id)
        serializer = self.get_serializer(query)
        return Response(serializer.data)

    @extend_schema(
        request=ProfileInfoSerializer,
        responses={
            200: None,
        },
        operation_id='update_profile_info',
        tags=['Authentication'],
    )
    @action(detail=False, methods=['PUT'], name='Update Profile Info ', url_path='update-profile-info')
    @parser_classes([FileUploadParser])
    def update_profile_info(self, request):
        user = Account.objects.get(pk=request.user.id)
        serializer = self.get_serializer(user, request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save()
        return Response({'message': message})

    @extend_schema(
        request=AccountActiveSerializer,
        responses={
            200: None,
        },
        operation_id='update_email',
        tags=['Authentication'],
    )
    @action(detail=False, methods=['POST'], name='Update Email', url_path='update-email')
    def update_email(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        update_email(serializer.validated_data['uuid'])
        return Response({'message': 'Email has been updated successfully!'})

    @extend_schema(
        request=ChangePasswordSerializer,
        responses={
            200: None,
        },
        operation_id='change_password',
        tags=['Authentication'],
    )
    @action(methods=['POST'], name='Change Password', detail=False, url_path='change-password')
    def change_password(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': self.request})
        serializer.is_valid(raise_exception=True)
        change_password(request.user, serializer.validated_data['new_password'])
        return Response({'message': 'Password successfully updated!'})

    @extend_schema(
        request=ResetPasswordSendSerializer,
        responses={
            200: None,
        },
        operation_id='reset_password_url_send',
        tags=['Authentication'],
    )
    @action(detail=False, methods=['POST'], name='Reset Passwort Email Send', url_path='reset-password-url-send')
    def reset_password_url_send(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        send_reset_password_email(serializer.validated_data['email'])
        return Response({'message': 'Reset password email send'})

    @extend_schema(
        request=ResetPasswordSendSerializer,
        responses={
            200: None,
        },
        operation_id='reset_password_secretkey_send',
        tags=['Authentication'],
    )
    @action(detail=False, methods=['POST'], name='Customer Passwort Reset Email Send',
            url_path='reset-password-secretkey-send')
    def reset_password_secretkey_send(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        send_reset_password_secretkey(serializer.validated_data['email'])
        return Response({'message': 'Reset password email send'})

    @extend_schema(
        request=ResetPasswordSerializer,
        responses={
            200: None,
        },
        operation_id='reset_password',
        tags=['Authentication'],
    )
    @action(detail=False, methods=['POST'], name='Reset Passwort', url_path='reset-password')
    def reset_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reset_password(**serializer.validated_data)
        return Response({'message': 'Your password has been reset successfully.'})

    @extend_schema(
        request=ResetCustomerPasswordSerializer,
        responses={
            200: None,
        },
        operation_id='reset_customer_password',
        tags=['Authentication'],
    )
    @action(detail=False, methods=['POST'], name='Reset Customer Passwort', url_path='reset-customer-password')
    def reset_customer_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reset_customer_password(**serializer.validated_data)
        return Response({'message': 'Your password has been reset successfully.'})

    @extend_schema(
        request=CreateNewUserSerializer,
        responses={
            200: None,
        },
        operation_id='create-new-user',
        tags=['Authentication'],
    )
    @action(detail=False, methods=['POST'], name='Create New User', url_path='create-new-user')
    def create_new_user(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'New user has been successfully created!'})

    @extend_schema(
        request=None,
        responses={
            200: UserListSerializer,
        },
        operation_id='users',
        tags=['Authentication'],
    )
    @action(detail=False, methods=['GET'], name='User List', url_path='users')
    def users(self, request):
        users = Account.objects.filter(is_superuser=False)
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=None,
        responses={
            200: UserSerializer,
        },
        operation_id='user_permissions',
        tags=['Authentication'],
    )
    @action(detail=False, methods=['GET'], name='User Permission List', url_path='user-permissions')
    def user_permissions(self, request, pk=None):
        user = get_object_or_404(Account, pk=request.user.id)
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @extend_schema(
        request=UserListSerializer,
        responses={
            201: UserListSerializer,
        },
        operation_id='set_user_role',
        tags=['Authentication'],
    )
    @action(detail=False, methods=['POST'], name='Set User Role', url_path='set-user-role')
    def set_user_roles(self, request):
        email = request.data.get('email', None)
        user = get_object_or_404(Account, email=email)
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['POST'], name='Generate Token for Customer by email',
            url_path='generate-token-for-customer')
    def generate_token_for_customer(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        login_data = login_customer(serializer.validated_data['email'])
        return Response(login_data)

    @extend_schema(
        request=CreateNewUserSerializer,
        responses={
            200: None,
        },
        operation_id='create-new-user',
        tags=['Authentication'],
    )
    @action(detail=False, methods=['POST'], name='Create New User', url_path='create-new-user')
    def create_new_user(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'New user has been successfully created!'})

    @extend_schema(
        request=SearchUsersSerializer,
        responses={
            200: None,
        },
        operation_id='search-users',
        tags=['Authentication'],
        parameters=[
            OpenApiParameter(
                name='email',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Email of the user to fetch users',
                required=True
            ),
        ]
    )
    @action(detail=False, methods=['GET'], name='Search Users', url_path='search-users')
    def search_users(self, request):
        email = request.query_params.get('email')
        if not email:
            raise ValidationError({'non_field_errors': ['Email is required in query parameter']})
        queryset = Account.objects.filter(email__icontains=email).exclude(
            Q(is_superuser=True) |
            Q(groups__name__in=["Admin", "Super Admin"])
        ).distinct()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
