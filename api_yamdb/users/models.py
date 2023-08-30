from django.contrib.auth.models import AbstractUser
from django.db import models

from users.validators import UsernameValidator

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'


class User(AbstractUser):
    """
    Модель пользователя. Расширяет стандартную модель AbstractUser.
    """
    ROLE_CHOICES = (
        (USER, USER),
        (MODERATOR, MODERATOR),
        (ADMIN, ADMIN),
    )
    username_validator = UsernameValidator()
    username = models.CharField(
        'Имя пользователя',
        max_length=150,
        unique=True,
        validators=[username_validator],
    )
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField('Email', max_length=254, unique=True)
    role = models.CharField(
        'Роль пользователя',
        choices=ROLE_CHOICES,
        max_length=max(len(role[1]) for role in ROLE_CHOICES), default=USER
    )
    bio = models.TextField('Биография', blank=True)
    confirmation_code = models.CharField(
        'Код подтверждения',
        max_length=100,
        null=True
    )

    REQUIRED_FIELDS = ['email']
    USERNAME_FIELDS = 'email'

    def __str__(self):
        """
        Строковое представление модели.
        """
        return str(self.username)

    @property
    def is_admin(self):
        return self.role == "admin" or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == "moderator"

    @property
    def is_user(self):
        return self.role == "user"
