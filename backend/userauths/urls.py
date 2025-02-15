from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView

from .views import RegistrationView, LoginView



urlpatterns = [
    path('user/register/', RegistrationView.as_view(), name='register'),
    path('user/login/', LoginView.as_view(), name='login'),
    path('user/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
