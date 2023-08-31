from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.views import (
    EmailActivation, UserViewSet, SignUp,
)

app_name = 'api'

router_v1 = SimpleRouter()
router_v1.register(
    'users',
    UserViewSet,
    basename='users',
)

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/signup/', SignUp.as_view(), name='sign_up'),
    path('v1/auth/token/', EmailActivation.as_view(), name='activation'),
]
