from django.contrib.auth.models import Group, Permission


class RoleFactory:
    """
    Factory class to create roles and assign permissions dynamically.
    """

    @staticmethod
    def create_role(name, permissions):
        """
        Create a new role (Group) and assign permissions.
        """
        group, created = Group.objects.get_or_create(name=name)
        perms = Permission.objects.filter(codename__in=permissions)
        group.permissions.set(perms)
        return group
