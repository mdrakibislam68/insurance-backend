from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.password_validation import validate_password
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken

from roles.models import CustomGroup
from .models import EmailUpdateRequest, PasswordReset
from .services.auth_module_services import Account
from .services.auth_viewsets_services import send_update_email_link
from .tasks import send_staff_invitation_email
from .utils.password_generator import generate_password
from .utils.token_generator import account_active_token_generator, reset_password_token_generator


def verify_access_token(token):
    try:
        access_token = AccessToken(token)
        return True
    except AuthenticationFailed:
        return False


class EmptySerializer(serializers.Serializer):
    pass


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        try:
            user = Account.objects.get(email__iexact=attrs['email'], is_active=True)
            if not user.check_password(attrs['password']):
                raise Exception('Wrong password!')
        except Exception:
            raise serializers.ValidationError({"password": "Email or password is incorrect"})
        return attrs


class CustomerLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs['email']
        password = attrs['password']

        return attrs


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    role = serializers.CharField()
    permissions = serializers.ListField(child=serializers.CharField())


class LoginResponseSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()
    user = UserSerializer()


class DefaultSignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True, validators=[validate_password])

    class Meta:
        model = Account
        fields = ('email', 'password')

    def validate(self, attrs):
        if attrs['email'] and Account.objects.filter(email__iexact=attrs['email']).exists():
            raise serializers.ValidationError({'email': 'An account already exists with this email.'})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Account.objects.create(is_active=False, **validated_data)
        user.set_password(password)
        user.save()
        return user


class CreateNewUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    role = serializers.PrimaryKeyRelatedField(queryset=CustomGroup.objects.all(), required=True)

    class Meta:
        model = Account
        fields = ('first_name', 'last_name', 'email', 'role')

    def validate(self, attrs):
        if attrs['email'] and Account.objects.filter(email__iexact=attrs['email'], is_staff=True).exists():
            raise serializers.ValidationError({'email': 'A staff account with this email already exists'})
        return attrs

    def create(self, validated_data):
        role = validated_data.pop('role')
        password = generate_password()
        is_new_user = False
        is_existing_user = Account.objects.filter(email__iexact=validated_data.get('email')).first()

        if is_existing_user:
            user = is_existing_user
            user.is_active = True
            user.is_staff = True
        else:
            is_new_user = True
            user = Account.objects.create(is_active=True, is_staff=True, **validated_data)
            user.set_password(password)
        user.save()
        user.groups.add(role)
        context = {
            'recipient_name': f'{user.first_name} {user.last_name}',
            'signin_url': f'{settings.FRONT_END_URL}/auth/login'
        }
        if is_new_user:
            context['email'] = user.email
            context['password'] = password

        send_staff_invitation_email.delay(user.email, context)
        return user


class AccountActiveSerializer(serializers.Serializer):
    uuid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['uuid'] is not None and attrs['token'] is not None:
            user_id = force_str(urlsafe_base64_decode(attrs['uuid']))
            user = Account.objects.get(pk=user_id)
            if not account_active_token_generator.check_token(user, attrs['token']):
                raise serializers.ValidationError({"non_field_errors": ["This verify URL is invalid or expired"]})
        return attrs


class AccountActiveResponseSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()
    message = serializers.CharField()
    user = UserSerializer()


class ResetPasswordSendSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        try:
            user = Account.objects.get(email__iexact=attrs['email'])
        except Account.DoesNotExist:
            raise serializers.ValidationError({"email": ["Account doesn't exist with this email."]})
        return attrs


# completed
class ResetPasswordSerializer(serializers.Serializer):
    uuid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    password2 = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password2": "Password do not match."})

        if attrs['uuid'] is not None and attrs['token'] is not None:
            decoded_value = force_str(urlsafe_base64_decode(attrs['uuid']))
            user_id, _ = decoded_value.split('-')
            user = Account.objects.get(pk=user_id)
            if not reset_password_token_generator.check_token(user, attrs['token']):
                raise serializers.ValidationError({"non_field_errors": ["Given token or uuid has expired"]})
        return attrs


class ResetCustomerPasswordSerializer(serializers.Serializer):
    uuid = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    password2 = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password2": "Password do not match."})

        if attrs['uuid'] is not None:
            reset_secret = PasswordReset.objects.filter(secretkey=attrs['uuid']).last()

            if not reset_secret:
                raise serializers.ValidationError({"uuid": "Invalid secret key"})

            decoded_value = force_str(urlsafe_base64_decode(attrs['uuid']))
            user_id, _ = decoded_value.split('-')
            user = Account.objects.get(pk=user_id)

            if not reset_password_token_generator.check_token(user, reset_secret.token):
                raise serializers.ValidationError({"non_field_errors": ["The given secret key has expired"]})
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()
    new_password_confirmation = serializers.CharField()

    def validate_old_password(self, value):
        current_user = self.context['request'].user
        if not current_user.check_password(value):
            raise serializers.ValidationError('Old password do not match')

        return value

    def validate(self, attrs):
        new_password = attrs.get('new_password', None)
        new_password_confirmation = attrs.get('new_password_confirmation', None)

        if not new_password == new_password_confirmation:
            raise serializers.ValidationError({
                'new_password_confirmation': ['The confirm password does not match']
            })

        return attrs


class DefaultProfileInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('avatar', 'email', 'first_name', 'last_name')

    def update(self, instance, validated_data):
        message = 'Profile has been updated!'
        email = validated_data.pop('email', None)
        if email and email != instance.email:
            message = 'Check your inbox to verify new email'
            update_request, created = EmailUpdateRequest.objects.get_or_create(user=instance)
            update_request.new_email = email
            update_request.save()
            send_update_email_link(instance)

        super().update(instance, validated_data)
        return message


class ModifiedJWTSerializer(serializers.Serializer):
    """
    Serializer for JWT Authentication.
    """
    access = serializers.CharField(source='access_token')
    refresh = serializers.CharField(source='refresh_token')
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        user_data = DefaultProfileInfoSerializer(obj['user'], context=self.context).data
        user = Account.objects.get(email__iexact=obj['user'])
        permission_list = []
        for group in user.groups.all():
            [permission_list.append(permission.codename) for permission in group.permissions.all() if
             permission.codename not in permission_list]
        user_data['permissions'] = permission_list
        return user_data


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'content_type']


class UserListSerializer(serializers.ModelSerializer):
    groups = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), many=True)

    class Meta:
        model = Account
        fields = ['id', 'email', 'groups']

    def update(self, instance, validated_data):
        groups = validated_data.pop('groups', None)
        if groups is not None:
            instance.groups.set(groups)
        return super().update(instance, validated_data)


class UserPermissionListSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = ['id', 'first_name', 'last_name', 'email', 'role', 'is_staff', 'is_superuser', 'permissions']

    def get_permissions(self, obj):
        return [] if obj.is_superuser else obj.get_all_permissions()

    def get_role(self, obj):
        return str(obj.groups.first())


class GenerateTokenForCustomerSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs['email']

        try:
            user = Account.objects.get(email__iexact=email, is_active=True)
        except Exception:
            raise serializers.ValidationError({"password": "Account does not exist with this email"})
        return attrs


class SearchUsersSerializer(serializers.Serializer):
    email = serializers.EmailField()


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'email', 'first_name', 'last_name', 'avatar']
