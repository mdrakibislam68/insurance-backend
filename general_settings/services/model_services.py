
def default_booking_value():
    return {
        "default_status": None,
        "statuses_that_block_timeslot": [],
        "statuses_on_pending_page": [],
        "statuses_hidden_on_calendar": [],
        "time_zone": "Europe/London",
        "time_system": "24",
        "date_format": "mm/dd/yyyy",
        "show_booking_end_time": True,
        "disable_verbose_output": False
    }

def default_restriction():
    return {
        "earliest_possible_booking": "",
        "latest_possible_booking": "",
        "max_future_bookings_per_customer": ""
    }

def default_currency_value():
    return {
        "symbol_before_price": "",
        "symbol_after_price": "",
        "thousand_separator": ",",
        "decimal_separator": ".",
        "number_of_decimals": 2
    }

def default_phone_settings():
    return {
        "show_phone_countries": "all",
        "default_phone_country": "gb",
        "included_phone_countries": [],
        "validate_phone_number": False,
        "format_phone_number": False,
        "show_dial_code_with_flag": True
    }

def default_timeslot_availability_logic_value():
    return {
        "one_agent_at_location": False,
        "one_location_at_time": True,
        "multiple_services_at_time": True
    }


def default_customer_value():
    return {
        "allow_customer_booking_reschedule": False,
        "limit_when_customer_can_reschedule": False,
        "reschedule_limit_value": 0,
        "reschedule_limit_unit": "minute",
        "status_on_customer_reschedule": "approved",
        "change_booking_status_on_customer_reschedule": False,
        "allow_customer_booking_cancellation": True,
        "set_cancel_restriction": True,
        "cancellation_limit_value": 24,
        "cancellation_limit_unit": 'hour',
        "enable_google_login": False,
        "enable_facebook_login": False,
    }


def default_setup_pages_value():
    return {
        "page_url_customer_dashboard": "",
        "page_url_customer_login": "",
    }


def default_peak_hours_value():
    return {
        "peak_hours_pricing_rule": "Peak hours session",
        "peak_hours_timeslot_label": "Peak hours session",
    }


def default_business_information_value():
    return {
        "company_name": "",
        "business_phone": "",
        "business_address": "",
    }


def general_settings_status_options():
    return [
        {
            "id": 1,
            "label": "Approved",
            "value": "approved"
        },
        {
            "id": 2,
            "label": "Pending Approval",
            "value": "pending"
        },
        {
            "id": 3,
            "label": "Cancelled by Customer",
            "value": "cancelled_by_customer"
        },
        {
            "id": 4,
            "label": "Cancelled by Staff",
            "value": "cancelled_by_staff",
        },
        {
            "id": 5,
            "label": "No Show",
            "value": "no_show"
        },
        {
            "id": 6,
            "label": "Completed",
            "value": "completed"
        },
        {
            "id": 7,
            "label": 'Customer Rescheduled',
            "value": 'customer_rescheduled',
        },
        {
            "id": 8,
            "label": 'Staff Rescheduled',
            "value": 'staff_rescheduled',
        },
    ]


def general_settings_time_system_options():
    return [
        {
            "id": 1,
            "label": "12-hour clock",
            "value": "12"
        },
        {
            "id": 2,
            "label": "24-hour clock",
            "value": "24"
        },
    ]


def general_settings_date_format_options():
    return [
        {
            "id": 1,
            "label": "MM/DD/YYYY",
            "value": "mm/dd/yyyy"
        },
        {
            "id": 2,
            "label": "MM.DD.YYYY",
            "value": "mm.dd.yyyy"
        },
        {
            "id": 3,
            "label": "DD/MM/YYYY",
            "value": "dd/mm/yyyy"
        },
        {
            "id": 4,
            "label": "DD.MM.YYYY",
            "value": "dd.mm.yyyy"
        },
        {
            "id": 5,
            "label": "YYYY-MM-DD",
            "value": "yyyy-mm-dd"
        },
    ]

def get_strf_date_format(value):
    format_map = {
        "mm/dd/yyyy": "%m/%d/%Y",
        "mm.dd.yyyy": "%m.%d.%Y",
        "dd/mm/yyyy": "%d/%m/%Y",
        "dd.mm.yyyy": "%d.%m.%Y",
        "yyyy-mm-dd": "%Y-%m-%d"
    }
    return format_map.get(value)

def general_settings_thousand_separator_options():
    return [
        {
            "id": 1,
            "label": "Comma (1,000)",
            "value": ","
        },
        {
            "id": 2,
            "label": "Dot (1.000)",
            "value": "."
        },
        {
            "id": 3,
            "label": "Space (1 000)",
            "value": " "
        },
        {
            "id": 4,
            "label": "None (1000)",
            "value": ""
        },
    ]


def general_settings_decimal_separator_options():
    return [
        {
            "id": 1,
            "label": "Dot (0.99)",
            "value": "."
        },
        {
            "id": 2,
            "label": "Comma (0,99)",
            "value": ","
        }
    ]


def general_settings_number_of_decimals_options():
    return [
        {
            "id": 1,
            "label": "0",
            "value": "0"
        },
        {
            "id": 2,
            "label": "1",
            "value": "1"
        },
        {
            "id": 3,
            "label": "2",
            "value": "2"
        },
        {
            "id": 4,
            "label": "3",
            "value": "3"
        },
        {
            "id": 5,
            "label": "4",
            "value": "4"
        },
    ]


def general_settings_time_duration_options():
    return [
        {
            "id": 1,
            "label": "minutes",
            "value": "minute"
        },
        {
            "id": 2,
            "label": "hours",
            "value": "hour"
        },
        {
            "id": 3,
            "label": "days",
            "value": "day"
        },
    ]
