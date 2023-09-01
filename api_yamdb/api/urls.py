from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TitleViewSet, GenreViewSet, CategoryViewSet

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='categories')
router.register('genres', GenreViewSet, basename='genres')
router.register('titles', TitleViewSet, basename='titles')

urlpatterns = [path('v1/', include(router.urls))]

from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.views import (
  EmailActivation,
  UserViewSet,
  SignUp,
  TitleViewSet,
  GenreViewSet,
  CategoryViewSet
)

app_name = 'api'

router_v1 = SimpleRouter()
router_v1.register('users', UserViewSet, basename='users')
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('titles', TitleViewSet, basename='titles')

# Определение URL-маршрутов для API
urlpatterns = [
    # Включение всех URL-маршрутов, созданных router_v1
    path('v1/', include(router_v1.urls)),
    # Эндпоинт для регистрации новых пользователей
    path('v1/auth/signup/', SignUp.as_view(), name='sign_up'),
    # Эндпоинт для активации и получения токена
    path('v1/auth/token/', EmailActivation.as_view(), name='activation'),
]

