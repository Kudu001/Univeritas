from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404

from apps.common.mixins import SuccessResponseMixin
from apps.accounts.permissions import IsSupervisor, IsDean, IsDeanOrSupervisor
from apps.accounts.enums import Role
from .models import ProjectGroup, GroupMembership
from .serializers import ProjectGroupSerializer, CreateGroupSerializer, AddMemberSerializer
from .services import create_group, add_member, remove_member, deactivate_group


class ProjectGroupListCreateView(SuccessResponseMixin, APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsSupervisor()]
        return [IsDeanOrSupervisor()]

    def get(self, request):
        user = request.user
        if user.role == Role.SUPERVISOR:
            qs = ProjectGroup.objects.filter(supervisor=user).select_related(
                'supervisor', 'department'
            ).prefetch_related('memberships__student')
        else:  # DEAN
            qs = ProjectGroup.objects.filter(
                department__faculty=user.faculty
            ).select_related('supervisor', 'department').prefetch_related('memberships__student')
        return self.success(data=ProjectGroupSerializer(qs, many=True).data)

    def post(self, request):
        serializer = CreateGroupSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        group = create_group(
            supervisor=request.user,
            department=data['department_id'],
            name=data['name'],
            academic_year=data['academic_year'],
            request=request,
        )
        return self.created(data=ProjectGroupSerializer(group).data)


class ProjectGroupDetailView(SuccessResponseMixin, APIView):
    permission_classes = [IsDeanOrSupervisor]

    def get(self, request, pk):
        group = self._get_group(request, pk)
        return self.success(data=ProjectGroupSerializer(group).data)

    def _get_group(self, request, pk):
        user = request.user
        if user.role == Role.SUPERVISOR:
            return get_object_or_404(ProjectGroup, pk=pk, supervisor=user)
        return get_object_or_404(ProjectGroup, pk=pk, department__faculty=user.faculty)


class ProjectGroupDeactivateView(SuccessResponseMixin, APIView):
    permission_classes = [IsDean]

    def patch(self, request, pk):
        group = get_object_or_404(ProjectGroup, pk=pk, department__faculty=request.user.faculty)
        if not group.is_active:
            return self.error(message='Group is already inactive.')
        deactivate_group(group, request.user, request)
        return self.success(message='Group deactivated.')


class GroupMemberCreateView(SuccessResponseMixin, APIView):
    permission_classes = [IsSupervisor]

    def post(self, request, pk):
        group = get_object_or_404(ProjectGroup, pk=pk, supervisor=request.user)
        serializer = AddMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            membership = add_member(
                group=group,
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                supervisor=request.user,
                request=request,
            )
        except ValueError as e:
            return self.error(message=str(e), status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
        from apps.accounts.serializers.user import UserBriefSerializer
        return self.created(
            data={
                'membership_id': str(membership.id),
                'student': UserBriefSerializer(membership.student).data,
            },
            message=f'Student added. Credentials sent to {data["email"]}',
        )


class GroupMemberDeleteView(SuccessResponseMixin, APIView):
    permission_classes = [IsSupervisor]

    def delete(self, request, pk, student_id):
        group = get_object_or_404(ProjectGroup, pk=pk, supervisor=request.user)
        from apps.accounts.models import CustomUser
        student = get_object_or_404(CustomUser, pk=student_id)
        try:
            remove_member(group, student, request.user, request)
        except ValueError as e:
            return self.error(message=str(e), status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
        return self.success(message='Student removed from group.')


class MyGroupView(SuccessResponseMixin, APIView):
    """Student-accessible endpoint to see their own group."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.accounts.enums import Role
        if request.user.role != Role.STUDENT:
            return self.error(message='Only students can access this endpoint.',
                              status_code=status.HTTP_403_FORBIDDEN)
        membership = GroupMembership.objects.filter(
            student=request.user
        ).select_related('group__supervisor', 'group__department').first()
        if not membership:
            return self.error(message='You are not assigned to any group.', status_code=status.HTTP_404_NOT_FOUND)
        return self.success(data=ProjectGroupSerializer(membership.group).data)
