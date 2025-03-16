from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Run seeder migration commands"

    def handle(self, *args, **kwargs):
        self.stdout.write("Running setup_booking_step...")
        call_command('setup_booking_step')

        self.stdout.write("Running setup_booking_table_column_setting...")
        call_command('setup_booking_table_column_setting')

        self.stdout.write("Running setup_countries...")
        call_command('setup_countries')

        self.stdout.write("Running setup_form_field_setting...")
        call_command('setup_form_field_setting')

        self.stdout.write("Running setup_general_setting...")
        call_command('setup_general_setting')

        self.stdout.write("Running setup_payment...")
        call_command('setup_payment')

        self.stdout.write("Running setup_roles...")
        call_command('setup_roles')

        self.stdout.write("Running setup_schedule...")
        call_command('setup_schedule')

        self.stdout.write("Running setup_webhook_actions...")
        call_command('setup_webhook_actions')

        self.stdout.write("All commands have been executed.")
