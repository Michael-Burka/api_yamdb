from django.contrib.auth.models import AbstractUser
from django.db import models

from users.authorization import UsernameValidator

USER = 'user'
ADMIN = 'admin'
MODERATOR = 'moderator'

ROLE_CHOICES = [
    (USER, USER),
    (ADMIN, ADMIN),
    (MODERATOR, MODERATOR),
]


class User(AbstractUser):
    """
    Модель пользователя. Расширяет стандартную модель AbstractUser.
    """
    username_validator = UsernameValidator()
    username = models.CharField(
        'Имя пользователя',
        max_length=150,
        unique=True,
        blank=False,
        null=False,
        help_text='Введите username',
        validators=[username_validator],
    )
    first_name = models.CharField('Имя', max_length=150, blank=True)
    last_name = models.CharField('Фамилия', max_length=150, blank=True)
    email = models.EmailField('Email', max_length=254, unique=True)
    role = models.CharField(
        'Роль пользователя',
        choices=ROLE_CHOICES,
        max_length=max(len(role[1]) for role in ROLE_CHOICES),
        help_text='Выберите роль пользователя',
        default=USER
    )
    bio = models.TextField('Биография', blank=True)
    confirmation_code = models.CharField(
        'Код подтверждения',
        max_length=100,
        null=True,
        blank=False,
        default='XXXX'
    )

    REQUIRED_FIELDS = ['email']
    USERNAME_FIELD = 'email'

    @property
    def is_admin(self):
        return self.role == ADMIN

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    @property
    def is_user(self):
        return self.role == USER

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        """
        Строковое представление модели.
        """
        return str(self.username)
