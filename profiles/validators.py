import datetime

from django.core.exceptions import ValidationError
from django.utils.timezone import now


def validate_date_of_birth(value):
    """
    Validates the date of birth to ensure it falls within the allowed range.
    The date must not be earlier than January 1, 1901, and must not be a future date.
    """
    min_date = datetime.date(1901, 1, 1)
    max_date = now().date()  # Prevent future dates
    if value < min_date or value > max_date:
        raise ValidationError("Please provide a valid date of birth.")
