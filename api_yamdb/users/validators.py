from django.core.validators import RegexValidator


class UsernameValidator(RegexValidator):
    """
    Валидатор для проверки допустимости символов в имени пользователя.
    """
    regex = r'^[\w.@+-]+$'
    flags = 0
