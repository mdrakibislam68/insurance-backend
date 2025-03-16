from django.core.management.base import BaseCommand

from general_settings.models import GeneralSettings


# from general_settings.services.model_services import (
#     default_booking_value,
#     default_currency_value,
#     default_timeslot_availability_logic_value,
#     default_customer_value,
#     default_setup_pages_value,
#     default_peak_hours_value,
#     default_business_information_value,
# )


class Command(BaseCommand):
    help = 'Seed the GeneralSettings model if no instances exist.'

    def handle(self, *args, **kwargs):
        if not GeneralSettings.objects.exists():
            GeneralSettings.objects.create(
                business_information={}
            )
            self.stdout.write(self.style.SUCCESS('Successfully seeded GeneralSettings model.'))
        else:
            self.stdout.write(self.style.SUCCESS('GeneralSettings already exist. No action taken.'))
