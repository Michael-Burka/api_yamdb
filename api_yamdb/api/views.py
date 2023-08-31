from django.db import IntegrityError

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView

from api.permissions import AdminWriteOnly
from api.serializers import (
    EmailActivationSerializer, AdminSerializer,
    SignUpSerializer, UserProfileSerializer
)
from users.authorization import get_tokens_for_user, send_mail_with_code
from users.models import User


class SignUp(APIView):
    """Представление для регистрации новых пользователей."""
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        """Регистрирует нового пользователя и отправляет код подтверждения."""
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
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
        token = get_tokens_for_user(user)
        return Response({'token': token},
                        status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ModelViewSet):
    """Представление для управления пользователями."""
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
        """Позволяет просматривать и редактировать свой профиль."""
        serializer = UserProfileSerializer(request.user)
        if request.method == 'PATCH':
            serializer = UserProfileSerializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_200_OK)
