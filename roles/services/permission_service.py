from django.contrib.auth.models import Permission

from roles.config.roles_permissions_config import DEFAULT_ROLES_PERMISSIONS


class PermissionService:
    queryset = Permission.objects.all()
    config = DEFAULT_ROLES_PERMISSIONS
    permissions = config['permissions']

    def __init__(self):
        self.permissions_dict = {perm.codename: perm for perm in self.queryset}

    def get_permissions(self):
        formatted_permissions = []
        for perm_group, perm_option in self.permissions.items():
            group_permissions = {
                'name': perm_group,
                'description': perm_option['description'],
                'actions': []
            }
            for action, assign_to_existing_groups in perm_option['actions'].items():
                codename = f'{action}_{perm_group.lower()}'
                permission = self.permissions_dict.get(codename)
                if permission:
                    formatted_permission = {
                        'id': permission.id,
                        'codename': permission.codename,
                        'action_name': action,
                    }
                    group_permissions['actions'].append(formatted_permission)
            formatted_permissions.append(group_permissions)

        return formatted_permissions
