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
    permission_classes = (AdminOrReadOnly,)
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
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    lookup_field = 'slug'
    search_fields = ('name',)


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

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)

        if len(serializer.validated_data.get('name', '')) > 256:
            raise ValidationError('Name cannot be longer than 256 characters.')

        self.perform_update(serializer)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)


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

