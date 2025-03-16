from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff


class IsGroupManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Group Manager').exists()


class IsAdminOrHasPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            if request.user.is_superuser or request.user.groups.filter(name__in=['Super Admin', 'Admin']).exists():
                return True

            required_perms = getattr(view, 'required_permissions', [])
            if not required_perms:
                return False
            user_perms = request.user.get_all_permissions()

            return all(perm in user_perms for perm in required_perms)
        return False
