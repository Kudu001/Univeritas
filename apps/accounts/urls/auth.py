from django.urls import path
from ..views.auth import LoginView, LogoutView, TokenRefreshView, PasswordChangeView

urlpatterns = [
    path('login/', LoginView.as_view(), name='auth-login'),
    path('refresh/', TokenRefreshView.as_view(), name='auth-refresh'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
    path('password/change/', PasswordChangeView.as_view(), name='auth-password-change'),
]
