from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

from roles.models import CustomGroup

User = get_user_model()


class RoleService:
    """
    Service class for handling role-based access control.
    """

    @staticmethod
    def assign_role(user: User, role_name: str):
        """
        Assign a role (Group) to a user.
        """
        group = CustomGroup.objects.get(name=role_name)
        user.groups.add(group)

    @staticmethod
    def remove_role(user: User, role_name: str):
        """
        Remove a role from a user.
        """
        group = CustomGroup.objects.get(name=role_name)
        user.groups.remove(group)

    @staticmethod
    def has_permission(user: User, permission_codename: str) -> bool:
        """
        Check if a user has a specific permission.
        """
        return user.has_perm(f"{permission_codename}")

    @staticmethod
    def get_user_roles(user: User):
        """
        Get all roles assigned to a user.
        """
        return user.groups.values_list("name", flat=True)
