from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.views import (
    EmailActivation, UserViewSet, SignUp,
)

app_name = 'api'

router_v1 = SimpleRouter()
# Регистрация маршрута для управления пользователями
# В этом маршруте будут доступны операции CRUD для пользователей
router_v1.register(
    'users',
    UserViewSet,
    basename='users',
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
