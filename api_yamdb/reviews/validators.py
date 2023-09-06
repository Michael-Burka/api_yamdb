import re
from datetime import datetime

from django.core.exceptions import ValidationError

def valildate_year(value):
    current_year = datetime.now().year
    if value > current_year:
        raise ValidationError(
            f'Введенное значение года ({value})'
            f'не может быть больше {current_year}'
        )

