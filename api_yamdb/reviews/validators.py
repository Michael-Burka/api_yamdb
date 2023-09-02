from datetime import datetime
import re

from django.core.exceptions import ValidationError

SLUG_REGEX = r'^[a-zA-Z0-9-]+$'


def valildate_year(value):
    current_year = datetime.now().year
    if value > current_year:
        raise ValidationError(
            f'Введенное значение года ({value})'
            f'не может быть больше {current_year}'
        )


def validate_slug(value):
    if not re.match(SLUG_REGEX, value):
        raise ValidationError(
            f'Введенное значение ({value})'
            f'не является валидным слагом'
        )
