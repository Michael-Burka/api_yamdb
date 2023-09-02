from django.db import IntegrityError
from django.shortcuts import get_object_or_404

from rest_framework import permissions, status, viewsets, mixins
from rest_framework.decorators import action  # для кастомных операций
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView  # для кастомных эндпоинтов

from api.permissions import AdminWriteOnly, IsAdminOrReadOnly, AuthorOrStaffWriteOrReadOnly
from reviews.models import Category, Genre, Title
from users.authorization import get_token, send_mail_with_code
from users.models import User
from api.serializers import (
    EmailActivationSerializer, AdminSerializer, SignUpSerializer,
    UserProfileSerializer, CategorySerializer, GenreSerializer,
    TitleSerializer, ReviewSerializer)


class SignUp(APIView):
    """Представление для регистрации новых пользователей."""
    permission_classes = (permissions.AllowAny,)  # доступ для всех

    def post(self, request):
        """Регистрирует нового пользователя и отправляет код подтверждения."""
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
    """Представление для активации электронной почты пользователя."""
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        """Проверяет код подтверждения и генерирует токен."""
        serializer = EmailActivationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(
            username=serializer.validated_data['username'])
        token = get_token(user)
        return Response({'token': token},
                        status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ModelViewSet):
    """Представление для управления пользователями."""
    queryset = User.objects.all()
    serializer_class = AdminSerializer
    # Только администраторы могут изменять данные.
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
        """
        Позволяет просматривать и редактировать свой профиль.
        Доступно только аутентифицированным пользователям.
        """
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


class CategoryViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin,
    mixins.CreateModelMixin, mixins.DestroyModelMixin,
):
    """
    Представление для управления категориями.
    Позволяет просматривать, создавать и удалять категории.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    lookup_field = 'slug'
    search_fields = ('name',)


class GenreViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin,
    mixins.CreateModelMixin, mixins.DestroyModelMixin,
):
    """
    Представление для управления жанрами.
    Позволяет просматривать, создавать и удалять жанры.
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    lookup_field = 'slug'
    search_fields = ('name',)


class TitleViewSet(viewsets.ModelViewSet):
    """
    Представление для управления произведениями.
    Позволяет просматривать, создавать, изменять и удалять произведения.
    """
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Представление для управления отзывов.
    """
    serializer_class = ReviewSerializer
    permission_classes = (AuthorOrStaffWriteOrReadOnly,)

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
