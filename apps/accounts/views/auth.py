from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from apps.common.mixins import SuccessResponseMixin
from apps.audit.services import log
from apps.audit.enums import AuditAction
from ..serializers.auth import LoginSerializer, PasswordChangeSerializer
from ..serializers.user import ProfileSerializer


class LoginView(SuccessResponseMixin, APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)
        log(actor=user, action=AuditAction.USER_LOGIN, obj=user, request=request)

        return self.success(data={
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': str(user.id),
                'email': user.email,
                'full_name': user.full_name,
                'role': user.role,
                'password_changed': user.password_changed,
            },
        })


class LogoutView(SuccessResponseMixin, APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            token = RefreshToken(request.data.get('refresh'))
            token.blacklist()
        except Exception:
            pass
        log(actor=request.user, action=AuditAction.USER_LOGOUT, obj=request.user, request=request)
        return self.success(message='Logged out successfully.')


class TokenRefreshView(SuccessResponseMixin, APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        from rest_framework_simplejwt.serializers import TokenRefreshSerializer
        serializer = TokenRefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.success(data={'access': serializer.validated_data['access']})


class PasswordChangeView(SuccessResponseMixin, APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.password_changed = True
        user.save(update_fields=['password', 'password_changed'])
        log(actor=user, action=AuditAction.PASSWORD_CHANGED, obj=user, request=request)
        return self.success(message='Password changed successfully.')
