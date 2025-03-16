from django.core.management.base import BaseCommand
from django.db import connection
from django.apps import apps
from django.db.utils import ProgrammingError, OperationalError
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Deletes data from specified tables and resets auto-increment indexes (PostgreSQL only), except superuser and staff accounts.'

    def handle(self, *args, **kwargs):

        # Get the custom user model (Account)
        Account = get_user_model()

        # Specify the models to truncate, excluding superuser and staff users in the Account model
        target_models = [Account, 'Booking', 'Transaction', 'Coupon']

        # Retrieve only the specified models by checking model classes
        all_models = [model for model in apps.get_models() if model in target_models or model.__name__ in target_models]

        for model in all_models:
            table_name = model._meta.db_table
            try:
                print(f"Clearing table {table_name}...")

                with connection.cursor() as cursor:
                    if model == Account:
                        # Delete dependent records from related tables manually
                        cursor.execute(f'TRUNCATE TABLE "processes_activitylogs" RESTART IDENTITY CASCADE;')
                        cursor.execute(f'TRUNCATE TABLE "payment_system_squarepayment" RESTART IDENTITY CASCADE;')
                        cursor.execute(f'TRUNCATE TABLE "payment_system_squarecustomer" RESTART IDENTITY CASCADE;')
                        cursor.execute(f'TRUNCATE TABLE "customers_customer" RESTART IDENTITY CASCADE;')

                        # Now delete only regular users from the Account table
                        cursor.execute(
                            f'DELETE FROM "{table_name}" WHERE NOT is_superuser AND NOT is_staff;'
                        )

                        # Reset ID sequence for remaining records
                        cursor.execute(
                            f'SELECT setval(pg_get_serial_sequence(\'"{table_name}"\', \'id\'), COALESCE(MAX(id), 1), MAX(id) IS NOT NULL) FROM "{table_name}";')
                    else:
                        # Truncate other specified tables
                        cursor.execute(f'TRUNCATE TABLE "{table_name}" RESTART IDENTITY CASCADE;')

            except (ProgrammingError, OperationalError) as e:
                print(f"Skipping {table_name}: {e}")

        self.stdout.write(self.style.SUCCESS("Specified data cleared, and indexes reset successfully (excluding superuser and staff)."))
