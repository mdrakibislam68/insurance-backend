import os
from django.core.management.base import BaseCommand
from django.apps import apps
from seeder.utils import camel_to_snake


SEEDER_TEMPLATE = '''from seeder.seeders.base_seeder import BaseSeeder
from {app_name}.factories.{factory_name_lower} import {factory_name}

class {seeder_name}(BaseSeeder):
	def run(self):
		print("Seeding data using {factory_name}...")
		{factory_name}().create(10)  # Generate 10 fake records
'''

class Command(BaseCommand):
	help = "Generate a Seeder file inside a Django app"

	def add_arguments(self, parser):
		parser.add_argument("app_name", type=str, help="Name of the Django app")
		parser.add_argument("seeder_name", type=str, help="Name of the Seeder class")
		parser.add_argument("factory_name", type=str, help="Name of the Factory class")

	def handle(self, *args, **kwargs):
		app_name = kwargs["app_name"]
		seeder_name = kwargs["seeder_name"]
		factory_name = kwargs["factory_name"]
		factory_name_lower = camel_to_snake(factory_name)

		# Ensure app exists
		try:
			app_config = apps.get_app_config(app_name)
		except LookupError:
			self.stdout.write(self.style.ERROR(f"App '{app_name}' does not exist."))
			return

		# Define seeder directory and file path
		seeder_dir = os.path.join(app_config.path, "seeders")
		seeder_file = os.path.join(seeder_dir, f"{camel_to_snake(seeder_name)}.py")

		# Create directories if they don't exist
		os.makedirs(seeder_dir, exist_ok=True)

		# Create Seeder file
		if not os.path.exists(seeder_file):
			with open(seeder_file, "w") as f:
				f.write(SEEDER_TEMPLATE.format(
					app_name=app_name,
					factory_name=factory_name,
					factory_name_lower=factory_name_lower,
					seeder_name=seeder_name
				))
			self.stdout.write(self.style.SUCCESS(f"Seeder created: {seeder_file}"))
		else:
			self.stdout.write(self.style.WARNING(f"Seeder already exists: {seeder_file}"))