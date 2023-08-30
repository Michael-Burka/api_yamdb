from datetime import datetime

from django.core.exceptions import ValidationError

def valildate_year(value):
    current_year = datetime.now().year
    if value > current_year:
        raise ValidationError(
                f'{value} is not a valid year!'
                f'Please enter a year before {current_year}')

