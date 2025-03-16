from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from roles.models import CustomGroup
from roles.config.roles_permissions_config import DEFAULT_ROLES_PERMISSIONS


class Command(BaseCommand):
    help = 'Set up default groups and permissions'

    def handle(self, *args, **kwargs):
        config = DEFAULT_ROLES_PERMISSIONS
        default_roles = config['roles']
        permissions = config['permissions']
        content_types_config = config['content_types']

        # Create content types
        content_types = {}
        for key, ct in content_types_config.items():
            content_type = ContentType.objects.get(app_label=ct['app_label'], model=ct['model'])
            content_types[key] = content_type

        # Create or update permissions
        new_permissions = []
        for perm_group, perm_options in permissions.items():
            for action, assign_to_existing_groups in perm_options['actions'].items():
                codename = f'{action}_{perm_group.lower()}'
                name = f'Can {action} {perm_group}'
                content_type = content_types.get(perm_group)
                permission, created = Permission.objects.get_or_create(
                    codename=codename,
                    content_type=content_type,
                    defaults={'name': name}
                )
                if created:
                    new_permissions.append((permission, assign_to_existing_groups))
                    self.stdout.write(self.style.SUCCESS(f'Permission {codename} created'))
                else:
                    if permission.name != name:
                        permission.name = name
                        permission.save()
                    self.stdout.write(self.style.SUCCESS(f'Permission {codename} synced'))

        for role in default_roles:
            group, created = CustomGroup.objects.get_or_create(
                name=role['name'],
                is_admin=role['is_admin'],
                is_default=role['is_default']
            )
            if role['name'] not in ['Super Admin', 'Admin']:
                role_permissions = Permission.objects.filter(codename__in=role['permissions'])
                group.permissions.set(role_permissions)

            # Assign new permissions to existing groups based on flags
            for permission, assign_to_existing_groups in new_permissions:
                if assign_to_existing_groups and role['name'] not in ['Super Admin', 'Admin']:
                    group.permissions.add(permission)

            if created:
                role_name = role['name']
                self.stdout.write(self.style.SUCCESS(f'{role_name} group created'))

        self.stdout.write(self.style.SUCCESS('Default groups and permissions set up successfully'))
