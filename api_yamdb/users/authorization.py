import logging
import random

from django.core.validators import RegexValidator
from rest_framework_simplejwt.tokens import RefreshToken
from smtplib import SMTPException
from django.conf import settings
from django.core.mail import send_mail


def get_tokens_for_user(user):
    """Генерирует и возвращает токены для заданного пользователя.

    Args:
        user: Пользователь, для которого необходимо сгенерировать токен.

    Returns:
        dict: Словарь, содержащий обновленный и доступный токены.
    """
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def send_mail_with_code(data):
    """Отправляет код подтверждения на указанный адрес электронной почты.

    Args:
        data (dict): Словарь с адресом электронной почты.

    Returns:
        str: Строка с кодом подтверждения.
    """
    email = data['email']
    confirmation_code = random.randint(1000, 9999)
    try:
        send_mail(
            'Код подтверждения',
            f'Ваш код подтверждения {confirmation_code}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False
        )
    except SMTPException as e:
        logging.error(f'Failed to send confirmation code email: {e}')
        raise Exception('Failed to send confirmation code email.')

    return str(confirmation_code)


class UsernameValidator(RegexValidator):
    """Валидатор для проверки допустимости имени пользователя.

    Используется регулярное выражение для проверки,
    что имя пользователя содержит только разрешенные символы.
    """
    regex = r'^[\w.@+-]+$'
    flags = 0
