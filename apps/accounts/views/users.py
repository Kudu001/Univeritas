from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404

from apps.common.mixins import SuccessResponseMixin
from apps.audit.services import log
from apps.audit.enums import AuditAction
from ..models import CustomUser
from ..enums import Role
from ..permissions import IsAdmin, IsDean
from ..serializers.user import (
    ProfileSerializer, CreateDeanSerializer, CreateSupervisorSerializer,
    DeanSerializer, SupervisorSerializer,
)
from ..services import create_user, deactivate_user, reactivate_user


class ProfileView(SuccessResponseMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return self.success(data=ProfileSerializer(request.user).data)

    def patch(self, request):
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        log(request.user, AuditAction.PROFILE_UPDATED, request.user, request=request)
        return self.success(data=serializer.data, message='Profile updated.')


class DeanListCreateView(SuccessResponseMixin, APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        deans = CustomUser.objects.filter(role=Role.DEAN).select_related('faculty').order_by('last_name')
        return self.success(data=DeanSerializer(deans, many=True).data)

    def post(self, request):
        serializer = CreateDeanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        faculty = data['faculty_id']  # already resolved to Faculty object

        # Check only one dean per faculty
        if CustomUser.objects.filter(role=Role.DEAN, faculty=faculty, is_active=True).exists():
            return self.error(
                message='A dean already exists for this faculty.',
                status_code=status.HTTP_409_CONFLICT,
            )

        user = create_user(
            role=Role.DEAN,
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            faculty=faculty,
            created_by=request.user,
            request=request,
        )
        return self.created(
            data=DeanSerializer(user).data,
            message=f'Dean account created. Credentials sent to {user.email}',
        )


class DeanDetailView(SuccessResponseMixin, APIView):
    def get_permissions(self):
        return [IsAdmin()]

    def get(self, request, pk):
        dean = get_object_or_404(CustomUser, pk=pk, role=Role.DEAN)
        return self.success(data=DeanSerializer(dean).data)


class DeanActivateView(SuccessResponseMixin, APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        dean = get_object_or_404(CustomUser, pk=pk, role=Role.DEAN)
        reactivate_user(dean, request.user, request)
        return self.success(message='Dean account reactivated.')


class DeanDeactivateView(SuccessResponseMixin, APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        dean = get_object_or_404(CustomUser, pk=pk, role=Role.DEAN)
        deactivate_user(dean, request.user, request)
        return self.success(message='Dean account deactivated.')


class SupervisorListCreateView(SuccessResponseMixin, APIView):
    permission_classes = [IsDean]

    def get(self, request):
        supervisors = (
            CustomUser.objects
            .filter(role=Role.SUPERVISOR, faculty=request.user.faculty)
            .select_related('faculty')
            .order_by('last_name')
        )
        return self.success(data=SupervisorSerializer(supervisors, many=True).data)

    def post(self, request):
        serializer = CreateSupervisorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = create_user(
            role=Role.SUPERVISOR,
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            faculty=request.user.faculty,
            created_by=request.user,
            request=request,
        )
        return self.created(
            data=SupervisorSerializer(user).data,
            message=f'Supervisor account created. Credentials sent to {user.email}',
        )


class SupervisorDetailView(SuccessResponseMixin, APIView):
    def get_permissions(self):
        return [IsDean()]

    def get(self, request, pk):
        supervisor = get_object_or_404(
            CustomUser, pk=pk, role=Role.SUPERVISOR, faculty=request.user.faculty
        )
        return self.success(data=SupervisorSerializer(supervisor).data)


class SupervisorActivateView(SuccessResponseMixin, APIView):
    permission_classes = [IsDean]

    def patch(self, request, pk):
        supervisor = get_object_or_404(
            CustomUser, pk=pk, role=Role.SUPERVISOR, faculty=request.user.faculty
        )
        reactivate_user(supervisor, request.user, request)
        return self.success(message='Supervisor account reactivated.')


class SupervisorDeactivateView(SuccessResponseMixin, APIView):
    permission_classes = [IsDean]

    def patch(self, request, pk):
        supervisor = get_object_or_404(
            CustomUser, pk=pk, role=Role.SUPERVISOR, faculty=request.user.faculty
        )
        deactivate_user(supervisor, request.user, request)
        return self.success(message='Supervisor account deactivated.')
