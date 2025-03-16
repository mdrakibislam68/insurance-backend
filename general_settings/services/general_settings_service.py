import re
from datetime import datetime, timedelta
from django.utils import timezone
from general_settings.models import GeneralSettings
from dateutil.relativedelta import relativedelta


class GeneralSettingsService:
    def __init__(self):
        self.general_settings = GeneralSettings.objects.first()
        self.customer_settings = self.general_settings.customer if self.general_settings else None
        self.setup_pages = self.general_settings.setup_pages if self.general_settings else None
        self.booking_settings = self.general_settings.booking if self.general_settings else None
        self.booking_restriction = self.general_settings.restriction if self.general_settings else None
        self.timeslot_availability_logic = self.general_settings.timeslot_availability_logic if self.general_settings else None
        self.business_information = self.general_settings.business_information if self.general_settings else None

    @staticmethod
    def is_date(date):
        try:
            return datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return False

    @staticmethod
    def restriction_time_value(time_string):
        current_datetime = timezone.now()
        match = re.match(r"([+-]?\d+)\s*(\w+)", time_string)
        if match:
            value = int(match.group(1))
            unit = match.group(2).lower()

            if unit in ['day', 'days']:
                result = current_datetime + timedelta(days=value)
            elif unit in ['week', 'weeks']:
                result = current_datetime + timedelta(weeks=value)
            elif unit in ['hour', 'hours']:
                result = current_datetime + timedelta(hours=value)
            elif unit in ['minute', 'minutes']:
                result = current_datetime + timedelta(minutes=value)
            elif unit in ['second', 'seconds']:
                result = current_datetime + timedelta(seconds=value)
            elif unit in ['month', 'months']:
                result = current_datetime + relativedelta(months=value)
            elif unit in ['year', 'years']:
                result = current_datetime + relativedelta(years=value)
            else:
                return False

            return result
        else:
            return False

    def get_dashboard_url(self):
        return self.setup_pages.get('page_url_customer_dashboard', '')

    def get_referral_page_url(self):
        return self.setup_pages.get('referral_page_url')

    def booking_restrictions(self, restriction_name=None):
        restrictions = {
            "latest_possible_booking": self.booking_restriction.get("latest_possible_booking", None),
            "earliest_possible_booking": self.booking_restriction.get("earliest_possible_booking", None),
            "max_future_bookings_per_customer": self.booking_restriction.get("max_future_bookings_per_customer", None),
        }
        if restriction_name:
            if restriction_name == 'max_future_bookings_per_customer':
                max_booking = restrictions.get(restriction_name)
                return int(max_booking) if max_booking else None

            restriction_date = self.is_date(restrictions.get(restriction_name))
            if restriction_date:
                return restriction_date

            restriction_time = self.restriction_time_value(restrictions.get(restriction_name))
            if restriction_time:
                return restriction_time

            return None
        return restrictions

    def get_booking_setting(self, status_name=None):
        all_booking_statues = {
            "time_zone": self.booking_settings.get("time_zone", ""),
            "date_format": self.booking_settings.get("date_format", ""),
            "time_system": self.booking_settings.get("time_system", ""),
            "default_status": self.booking_settings.get("default_status", ""),
            "statuses_on_pending_page": self.booking_settings.get("statuses_on_pending_page", []),
            "statuses_hidden_on_calendar": self.booking_settings.get("statuses_hidden_on_calendar", []),
            "statuses_that_block_timeslot": self.booking_settings.get("statuses_that_block_timeslot", []),
        }
        if status_name:
            return all_booking_statues.get(status_name)
        return all_booking_statues

    def get_timeslot_availability_logic(self, logic_name=None):
        all_timeslot_logic = {
            "time_zone": self.booking_settings.get("time_zone", ""),
            'one_location_at_time': self.timeslot_availability_logic.get("one_location_at_time", False),
            'one_agent_at_location': self.timeslot_availability_logic.get("one_agent_at_location", False),
            'multiple_services_at_time': self.timeslot_availability_logic.get("multiple_services_at_time", False),
        }
        if logic_name:
            return all_timeslot_logic.get(logic_name)
        return all_timeslot_logic

    def get_compony_logo_url(self):
        if not self.general_settings:
            return None
        return self.general_settings.company_logo.url if self.general_settings.company_logo else None

    def get_business_info(self):
        return self.general_settings.business_information if self.general_settings else None

