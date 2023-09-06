from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView

from api.filters import TitleFilter
from api.permissions import (AdminOrReadOnly, AdminWriteOnly,
                             AuthorOrStaffWriteOrReadOnly)
from api.serializers import (AdminSerializer, CategorySerializer,
                             CommentSerializer, EmailActivationSerializer,
                             GenreSerializer, ReviewSerializer,
                             SignUpSerializer, TitleReadSerializer,
                             TitleSerializer, UserProfileSerializer)
from reviews.models import Category, Genre, Review, Title
from users.authorization import get_token, send_mail_with_code
from users.models import User


class SignUp(APIView):
    """
    Класс для регистрации новых пользователей.
    ...
    Атрибуты
    --------
    permission_classes : tuple
        классы разрешений для доступа к представлению

    Методы
    ------
    post(request):
        Регистрирует нового пользователя и отправляет код подтверждения.
    """

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            # Пытаемся получить/создать пользователя с указанными именем/почтой
            user = User.objects.get_or_create(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email'],
            )[0]
        except IntegrityError:
            return Response(
                'Пользователь с таким именем или почтой уже существует.',
                status=status.HTTP_400_BAD_REQUEST
            )
        user.confirmation_code = send_mail_with_code(request.data)
        user.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class EmailActivation(APIView):
    """
    Класс для активации электронной почты пользователя.
    ...
    Атрибуты
    --------
    permission_classes : tuple
        классы разрешений для доступа к представлению

    Методы
    ------
    post(request):
        Проверяет код подтверждения и генерирует токен.
    """

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = EmailActivationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
         user = User.objects.get(
                    username__iexact=serializer.validated_data['username']
                )
        except User.DoesNotExist:
            raise ValidationError({"Ошибка": 'Пользователь не найден'})
        token = get_token(user)
        return Response({'token': token},
                        status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ModelViewSet):
    """
    Класс для управления пользователями.
    ...
    Атрибуты
    --------
    queryset : QuerySet
        набор данных всех пользователей
    serializer_class : Serializer
        класс сериализатора для управления пользователями
    permission_classes : tuple
        классы разрешений для доступа к представлению
    filter_backends : tuple
        классы фильтрации для запросов
    lookup_field : str
        поле для поиска пользователя
    search_fields : tuple
        поля для поиска
    http_method_names : list
        поддерживаемые HTTP-методы

    Методы
    ------
    my_profile(request):
        Позволяет просматривать и редактировать свой профиль.
        Доступно только аутентифицированным пользователям.

    """

    queryset = User.objects.all()
    serializer_class = AdminSerializer
    permission_classes = (AdminWriteOnly,)
    filter_backends = (SearchFilter,)
    lookup_field = 'username'
    search_fields = ('username',)
    http_method_names = ['get', 'post', 'head', 'patch', 'delete']

    @action(
        detail=False, methods=['get', 'patch'],
        url_path='me', url_name='me',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def my_profile(self, request):
        serializer = UserProfileSerializer(request.user)
        if request.method == 'PATCH':
            # При PATCH-запросе профиль можно частично обновить.
            serializer = UserProfileSerializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryGenreBaseViewSet(
        viewsets.GenericViewSet, mixins.ListModelMixin,
        mixins.CreateModelMixin, mixins.DestroyModelMixin,
):
    """
    Базовое представление для управления категориями и жанрами.
    """
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    lookup_field = 'slug'
    search_fields = ('name',)


class CategoryViewSet(CategoryGenreBaseViewSet):
    """
    Представление для управления категориями.
    Позволяет просматривать, создавать и удалять категории.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenreBaseViewSet):
    """
    Представление для управления жанрами.
    Позволяет просматривать, создавать и удалять жанры.
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """
    Представление для управления произведениями.
    Позволяет просматривать, создавать, изменять и удалять произведения.
    """
    queryset = (Title.objects
                .annotate(rating=Avg('reviews__score'))
                .order_by('name'))
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    serializer_class = TitleSerializer
    http_method_names = ['get', 'post', 'delete', 'patch']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Представление для управления отзывов.
    """
    serializer_class = ReviewSerializer
    permission_classes = (AuthorOrStaffWriteOrReadOnly,)
    http_method_names = ['get', 'post', 'delete', 'patch']

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """
    Представление для управления комментариями.
    """
    serializer_class = CommentSerializer
    permission_classes = (AuthorOrStaffWriteOrReadOnly,)
    http_method_names = ['get', 'post', 'delete', 'patch']

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=self.get_review()
        )
