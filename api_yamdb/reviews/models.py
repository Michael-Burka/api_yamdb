from enum import unique
from django.contrib.auth.models import AbstractUser
from django.db import models

SLUG_MAX_LENGTH = 50
NAME_MAX_LENGTH = 150


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
            )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    name = models.CharField(
            max_length=256,
            verbose_name='Название произведения',
            help_text='Введите название произведения',
            db_index=True,
            )
    year = models.PositiveSmallIntegerField(
            verbose_name='Год релиза',
            help_text='Введите год релиза произведения',
            db_index=True,
            )
    description = models.TextField(
            verbose_name='Описание произведения',
            help_text='Введите описание произведения',
            blank=True,
            null=True,
            )
    category = models.ForeignKey(
            Category,
            on_delete=models.SET_NULL,
            verbose_name='Категория',
            help_text='Выберите категорию произведения',
            )
    genre = models.ManyToManyField(
            Genre,
            null=True,
            verbose_name='Жанр',
            help_text='Выберите жанр произведения',
            )
    
    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'


class Review(models.Model):
    pass


class Comment(models.Model):
    pass 
