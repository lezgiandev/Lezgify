from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

from . import views

app_name = 'user'

urlpatterns = [
    path(
        'register/',
        views.RegisterView.as_view(),
        name='register'
    ),
    path(
        'change-password/',
        views.ChangePasswordView.as_view(),
        name='change-password'
    ),
    path(
        'token/',
        TokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),
    path(
        'token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'
    ),
]
