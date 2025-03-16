from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from rest_framework import serializers

from roles.models import CustomGroup

Account = get_user_model()


class RoleAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'first_name', 'last_name', 'email', 'avatar', 'is_superuser', 'is_active', 'last_login']


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename']


class GroupSerializer(serializers.ModelSerializer):
    permissions = serializers.PrimaryKeyRelatedField(queryset=Permission.objects.all(), many=True)
    users_count = serializers.IntegerField(source='user_set.count', read_only=True)

    class Meta:
        model = CustomGroup
        fields = ['id', 'name', 'is_admin', 'is_default', 'description', 'permissions', 'users_count']


class PermissionActionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    codename = serializers.CharField()
    action_name = serializers.CharField()


class PermissionGroupSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()
    actions = PermissionActionSerializer(many=True)


class SetUserPermissionsSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    role = serializers.PrimaryKeyRelatedField(
        queryset=CustomGroup.objects.all().exclude(name__in=['Admin', 'Super Admin']), required=False)
    permissions = serializers.PrimaryKeyRelatedField(queryset=Permission.objects.all(), many=True)

    def create(self, validated_data):
        email = validated_data.get('email')
        role = validated_data.get('role')
        permissions = validated_data.get('permissions', [])

        try:
            user = Account.objects.get(email__iexact=email)
        except Account.DoesNotExist:
            raise serializers.ValidationError({"non_field_errors": ["User not found with this email"]})

        if not user.groups.filter(name=role.name).exists():
            user.groups.set([role])
        user.user_permissions.set(permissions)
        user.save()

        return user


class RoleUsersSerializer(serializers.ModelSerializer):
    users = RoleAccountSerializer(many=True, source='user_set', read_only=True)

    class Meta:
        model = CustomGroup
        fields = ['users']


class RoleOptionListSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source='name', read_only=True)
    value = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = CustomGroup
        fields = ('id', 'label', 'value')


class UserPermissionsSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    permissions = serializers.ListField(child=serializers.IntegerField(), read_only=True)


class UserDeleteSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        current_user = self.context.get('request').user

        # Prevent self-deletion
        if current_user.email == attrs['email']:
            raise serializers.ValidationError({"non_field_errors": ["You cannot delete your own account."]})

        # Retrieve the user to delete
        user_to_delete = Account.objects.filter(email=attrs['email']).first()
        if not user_to_delete:
            raise serializers.ValidationError({"non_field_errors": ["User not found."]})

        # Super Admin can delete anyone
        if current_user.groups.filter(name='Super Admin').exists():
            return attrs

        # Admin can delete users and other Admins except Super Admins
        if current_user.groups.filter(name='Admin').exists():
            if user_to_delete.groups.filter(name='Super Admin').exists():
                raise serializers.ValidationError(
                    {"non_field_errors": ["Admins cannot delete Super Admins."]})
            return attrs

        # If not Super Admin or Admin, deny permission
        raise serializers.ValidationError({"non_field_errors": ["You don't have permission to perform this action."]})
