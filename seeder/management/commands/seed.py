import importlib
import os
from django.core.management.base import BaseCommand
from django.apps import apps

class Command(BaseCommand):
    help = "Seed the database with fake data"

    def add_arguments(self, parser):
        parser.add_argument(
            "seeder_name", nargs="?", type=str, default=None,
            help="Optional: Name of a specific seeder file (e.g., blog_seeder)."
        )

    def handle(self, *args, **kwargs):
        seeder_name = kwargs["seeder_name"]
        self.stdout.write(self.style.WARNING("Seeding database..."))

        for app_config in apps.get_app_configs():
            seeder_path = f"{app_config.name}.seeders"
            seeder_dir = os.path.join(app_config.path, "seeders")

            if os.path.exists(seeder_dir) and os.path.isdir(seeder_dir):
                for filename in os.listdir(seeder_dir):
                    if filename.endswith("_seeder.py"):
                        module_name = filename[:-3]  # Remove ".py"
                        
                        # If a specific seeder is requested, only run that one
                        if seeder_name and module_name != seeder_name:
                            continue

                        full_module_name = f"{seeder_path}.{module_name}"
                        module = importlib.import_module(full_module_name)

                        for attr in dir(module):
                            seeder_class = getattr(module, attr)
                            if isinstance(seeder_class, type) and issubclass(seeder_class, object):
                                try:
                                    if issubclass(seeder_class, object) and hasattr(seeder_class, "run"):
                                        self.stdout.write(self.style.SUCCESS(f"Running {seeder_class.__name__}..."))
                                        seeder_instance = seeder_class()
                                        seeder_instance.run()
                                except TypeError:
                                    pass  # Ignore base classes

        self.stdout.write(self.style.SUCCESS("Database seeding complete!"))