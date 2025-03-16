import uuid
from datetime import datetime, timedelta
from urllib.parse import quote

from django.utils import timezone


def generate_code():
    return uuid.uuid4().hex[:7].upper()


def get_unique_booking_code():
    code = generate_code()
    return code


def calculate_duration(end_datetime, start_datetime):
    duration = end_datetime - start_datetime
    duration_minute = int(duration.seconds / 60)
    return duration_minute


def get_aware_datetime(date_time):
    if not date_time:
        return date_time
    date_time = datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
    return timezone.make_aware(date_time)


def convert_date_format(format_str):
    replacements = {
        'd': 'dd',
        'm': 'mm',
        'Y': 'yyyy'
    }

    for short, long in replacements.items():
        format_str = format_str.replace(short, long)

    return format_str


def generate_safe_cache_key(*parts):
    """
    Generates a safe cache key by concatenating the parts and URL-encoding the result.
    """
    key = ":".join(map(str, parts))
    return quote(key, safe="")


def get_previous_date_range(given_start_date, given_end_date):
    # Convert string dates to datetime objects
    start_date = datetime.strptime(given_start_date, '%Y-%m-%d')
    end_date = datetime.strptime(given_end_date, '%Y-%m-%d')

    # Calculate the duration of the date range
    duration = end_date - start_date
    duration = duration + timedelta(days=1)
    # Calculate the previous date range with time
    previous_start_date = start_date - duration
    previous_end_date = end_date - duration
    previous_end_date = previous_end_date.replace(hour=23, minute=59, second=59)
    # Return the results
    return previous_start_date.strftime('%Y-%m-%d %H:%M:%S'), previous_end_date.strftime('%Y-%m-%d %H:%M:%S')


def get_current_date_range(given_start_date, given_end_date):
    current_start_date = f'{given_start_date} 00:00:00'
    current_end_date = f'{given_end_date} 23:59:59'

    # Return the results
    return current_start_date, current_end_date


def calculate_increase_decrease(previous_total, current_total):
    if previous_total != 0:
        percentage_change = ((current_total - previous_total) / previous_total) * 100
    else:
        percentage_change = float('inf') if current_total > 0 else 0

    # Determine the sign for the percentage change
    sign = '+' if percentage_change > 0 else '-' if percentage_change < 0 else ''

    if percentage_change == float('inf'):
        return f"{sign}100.00%"
    else:
        return f"{sign}{abs(percentage_change):.2f}%"


def generate_unique_code(prefix=None, length=6):
    """Generate a unique gift code with an optional prefix."""
    unique_part = str(uuid.uuid4()).replace('-', '')[:length].upper()
    return f"{prefix}{unique_part}" if prefix else unique_part
