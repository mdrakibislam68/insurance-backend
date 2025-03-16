import os
from django.core.management.base import BaseCommand
from django.apps import apps
from seeder.utils import camel_to_snake


FACTORY_TEMPLATE = '''from seeder.factories.base_factory import BaseFactory
from {app_name}.models import {model_name}

class {factory_name}(BaseFactory):
	def create(self, count=1, **overrides):
		objects = []

		for _ in range(count):
			data = {}
			data.update(overrides)

			try:
				objects.append({model_name}(**data))
			except Exception as e:
				print('Error creating {model_name} factory:', e)

		return {model_name}.objects.bulk_create(objects)
'''

class Command(BaseCommand):
    help = "Generate a Factory file inside a Django app"

    def add_arguments(self, parser):
        parser.add_argument("app_name", type=str, help="Name of the Django app")
        parser.add_argument("factory_name", type=str, help="Name of the Factory class")

    def handle(self, *args, **kwargs):
        app_name = kwargs["app_name"]
        factory_name = kwargs["factory_name"]
        factory_name_lower = camel_to_snake(factory_name)
        model_name = factory_name.replace("Factory", "")  # Derive model name

        # Ensure app exists
        try:
            app_config = apps.get_app_config(app_name)
        except LookupError:
            self.stdout.write(self.style.ERROR(f"App '{app_name}' does not exist."))
            return

        # Define factory directory and file path
        factory_dir = os.path.join(app_config.path, "factories")
        factory_file = os.path.join(factory_dir, f"{factory_name_lower}.py")

        # Create directories if they don't exist
        os.makedirs(factory_dir, exist_ok=True)

        # Create Factory file
        if not os.path.exists(factory_file):
            with open(factory_file, "w") as f:
                f.write(FACTORY_TEMPLATE.format(
                    app_name=app_name,
                    factory_name=factory_name,
                    model_name=model_name
                ))
            self.stdout.write(self.style.SUCCESS(f"Factory created: {factory_file}"))
        else:
            self.stdout.write(self.style.WARNING(f"Factory already exists: {factory_file}"))