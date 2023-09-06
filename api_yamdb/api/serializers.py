from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title
from users.models import ROLE_CHOICES, User


def check_username_exists(username):
    """Проверка наличия пользователя с заданным именем пользователя.

    Если пользователя не существует, выбрасывает Http404.
    """
    try:
        User.objects.get(username__iexact=username)
    except User.DoesNotExist:
        raise Http404(f'Пользователь `{username}` не найден.')


def check_username_email_pair(username, email):
    """Проверка соответствия имени пользователя и адреса электронной почты.

    Если email не соответствует заданному пользователю,
    выбрасывает ValidationError.
    """
    try:
        user = User.objects.get(username__iexact=username)
    except User.DoesNotExist:
        raise ValidationError({"message": "Username не существует"})
    if user.email != email:
        raise ValidationError({"message": "Неверный email"})


class SignUpSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации нового пользователя."""
    username = serializers.SlugField(max_length=150)
    email = serializers.EmailField(max_length=254)

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate_username(self, username):
        """Проверка допустимости имени пользователя."""
        if username.lower() == 'me':
            raise ValidationError({"message": "Недопустимый username"})
        return username

    def validate(self, data):
        """Общая проверка валидности данных."""
        if User.objects.filter(username=data['username']).exists():
            check_username_email_pair(data['username'], data['email'])
        return data


class EmailActivationSerializer(serializers.ModelSerializer):
    """Сериализатор для активации пользователя по электронной почте."""
    username = serializers.SlugField(max_length=150)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')

    def validate_username(self, username):
        """Проверка существования имени пользователя."""
        check_username_exists(username)
        return username

    def validate(self, data):
        """Проверка кода активации."""
        try:
            user = User.objects.get(username__iexact=data['username'])
        except User.DoesNotExist:
            raise ValidationError({"Ошибка": 'Пользователь не найден'})
        if data['confirmation_code'] != user.confirmation_code:
            raise ValidationError({"Ошибка": 'Неверный код подтверждения'})


class AdminSerializer(serializers.ModelSerializer):
    """Сериализатор для административных задач управления пользователями."""
    role = serializers.ChoiceField(choices=ROLE_CHOICES, required=False)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role',
        )


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения профиля пользователя."""
    username = serializers.SlugField(max_length=150)
    email = serializers.EmailField(max_length=254)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role',
        )
        read_only_fields = ('username', 'email', 'role',)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        exclude = ('id',)


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True,
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug',
    )

    class Meta:
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')
        model = Title

    def validate_name(self, value):
        if len(value) > 256:
            raise serializers.ValidationError('Name cannot be longer than 256 characters.')
        return value


class TitleReadSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.FloatField()

    class Meta:
        fields = (
            'id',
            'name',
            'year',
            'description',
            'genre',
            'category',
            'rating',
        )
        read_only_fields = fields
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault())

    score = serializers.IntegerField(
        min_value=1,
        max_value=10,
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        author = self.context['request'].user
        title = get_object_or_404(
            Title,
            id=self.context['view'].kwargs.get('title_id')
        )
        if Review.objects.filter(
                author=author, title=title).exists():
            raise serializers.ValidationError(
                'Вы уже написали отзыв к этому произведению!'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment
