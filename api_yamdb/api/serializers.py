from django.http import Http404
from django.core.exceptions import ValidationError
from rest_framework import serializers, validators

from users.models import ROLE_CHOICES, User
from reviews.models import Category, Comment, Genre, Review, Title


def check_username_exists(username):
    """Проверка наличия пользователя с заданным именем пользователя.

    Если пользователя не существует, выбрасывает Http404.
    """

    try:
        User.objects.get(username__iexact=username)
    except User.DoesNotExist:
        raise Http404(f"Пользователь `{username}` не найден.")


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


class CurrentTitleDefault(serializers.CurrentUserDefault):
    """Значение по умолчанию для поля title."""

    def __call__(self, serializer_field):
        return serializer_field.context["view"].kwargs.get("title_id")


class SignUpSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации нового пользователя."""

    username = serializers.SlugField(max_length=150)
    email = serializers.EmailField(max_length=254)

    class Meta:
        model = User
        fields = ("username", "email")

    def validate_username(self, username):
        """Проверка допустимости имени пользователя."""
        if username.lower() == "me":
            raise ValidationError({"message": "Недопустимый username"})
        return username

    def validate(self, data):
        """Общая проверка валидности данных."""
        if User.objects.filter(username__iexact=data["username"]).exists():
            check_username_email_pair(data["username"], data["email"])
        return data


class EmailActivationSerializer(serializers.ModelSerializer):
    """Сериализатор для активации пользователя по электронной почте."""

    username = serializers.SlugField(max_length=150)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ("username", "confirmation_code")

    def validate_username(self, username):
        """Проверка существования имени пользователя."""
        check_username_exists(username)
        return username

    def validate(self, data):
        """Проверка кода активации."""
        try:
            user = User.objects.get(username__iexact=data["username"])
        except User.DoesNotExist:
            raise ValidationError({"Ошибка": "Пользователь не найден"})
        if data["confirmation_code"] != user.confirmation_code:
            raise ValidationError({"Ошибка": "Неверный код подтверждения"})


class AdminSerializer(serializers.ModelSerializer):
    """Сериализатор для административных задач управления пользователями."""

    role = serializers.ChoiceField(choices=ROLE_CHOICES, required=False)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        )


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения профиля пользователя."""

    username = serializers.SlugField(max_length=150)
    email = serializers.EmailField(max_length=254)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        )
        read_only_fields = (
            "username",
            "email",
            "role",
        )


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ("id",)


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        exclude = ("id",)


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field="slug",
        many=True,
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field="slug",
    )

    class Meta:
        fields = ("id", "name", "year", "description", "genre", "category")
        model = Title

    def validate_name(self, value):
        if len(value) > 256:
            raise serializers.ValidationError(
                "Name cannot be longer than 256 characters."
            )
        return value


class TitleReadSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.FloatField()

    class Meta:
        fields = (
            "id",
            "name",
            "year",
            "description",
            "genre",
            "category",
            "rating",
        )
        read_only_fields = fields
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(
        read_only=True, default=serializers.CurrentUserDefault()
    )
    title = serializers.StringRelatedField(
        read_only=True, default=CurrentTitleDefault()
    )

    class Meta:
        fields = ("id", "text", "author", "title", "score", "pub_date")
        model = Review
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=("title", "author"),
                message="Вы уже написали отзыв к этому произведению!",
            ),
        ]


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field="username", read_only=True, default=serializers.CurrentUserDefault()
    )

    class Meta:
        fields = ("id", "text", "author", "pub_date")
        model = Comment
