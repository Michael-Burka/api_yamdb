from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.views import (CategoryViewSet, CommentViewSet, EmailActivation,
                       GenreViewSet, ReviewViewSet, SignUp, TitleViewSet,
                       UserViewSet
                       )

app_name = 'api'

router_v1 = SimpleRouter()
router_v1.register('users', UserViewSet, basename='users')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet, basename='reviews'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments'
)

# Определение URL-маршрутов для API
urlpatterns = [
    # Включение всех URL-маршрутов, созданных router_v1
    path('v1/', include(router_v1.urls)),
    # Эндпоинт для регистрации новых пользователей
    path('v1/auth/signup/', SignUp.as_view(), name='sign_up'),
    # Эндпоинт для активации и получения токена
    path('v1/auth/token/', EmailActivation.as_view(), name='activation'),
]
