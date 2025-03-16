from django.core.management.base import BaseCommand
from roles.models import CustomGroup
from roles.config.roles_permissions_config import DEFAULT_ROLES_PERMISSIONS


class Command(BaseCommand):
    help = 'Set up default roles'

    def handle(self, *args, **kwargs):
        config = DEFAULT_ROLES_PERMISSIONS
        default_roles = config['roles']

        for role in default_roles:
            group, created = CustomGroup.objects.get_or_create(
                name=role['name'],
                is_admin=role['is_admin'],
                is_default=role['is_default']
            )
            if created:
                role_name = role['name']
                self.stdout.write(self.style.SUCCESS(f'{role_name} roles created'))

        self.stdout.write(self.style.SUCCESS('Default roles set up successfully'))
