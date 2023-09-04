from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from users.models import User
from reviews.validators import validate_slug, valildate_year

SLUG_MAX_LENGTH = 50
NAME_MAX_LENGTH = 256


class Category(models.Model):
    name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name='Название категории',
        help_text='Введите название категории',
    )
    slug = models.SlugField(
        max_length=SLUG_MAX_LENGTH,
        verbose_name='Слаг категории',
        unique=True,
        help_text='Введите слаг категории',
        validators=[validate_slug],
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(models.Model):
    name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name='Название жанра',
        help_text='Введите название жанра',
    )
    slug = models.SlugField(
        max_length=SLUG_MAX_LENGTH,
        verbose_name='Слаг жанра',
        unique=True,
        help_text='Введите слаг жанра',
        validators=[validate_slug],
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name='Название произведения',
        help_text='Введите название произведения',
        db_index=True,
    )
    year = models.PositiveSmallIntegerField(
        verbose_name='Год выпуска',
        help_text='Введите год выпуска произведения',
        db_index=True,
        validators=[valildate_year],
    )
    description = models.TextField(
        verbose_name='Описание произведения',
        help_text='Введите описание произведения',
        blank=True,
        null=True,
    )
    category = models.ForeignKey(
        Category,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Категория',
        help_text='Выберите категорию произведения',
        related_name='titles',
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр',
        help_text='Выберите жанр произведения',
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'


class Review(models.Model):
    text = models.TextField('Текст отзыва')
    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка',
        validators=(MinValueValidator(1), MaxValueValidator(10)),
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    def __str__(self) -> str:
        return self.text[:10]

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_author_title_review',
            )
        ]


class Comment(models.Model):
    text = models.TextField('Комментарий')
    review = models.ForeignKey(
        Review,
        verbose_name='Отзыв',
        on_delete=models.CASCADE,
        related_name='comments',
        db_index=True
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор комментария',
        on_delete=models.CASCADE,
        related_name='comments',
        db_index=True
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    def __str__(self) -> str:
        return self.text[:10]

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
