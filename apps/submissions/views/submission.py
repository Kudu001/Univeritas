from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404

from apps.common.mixins import SuccessResponseMixin
from apps.accounts.permissions import IsStudent, IsSupervisor, IsDean
from apps.accounts.enums import Role
from ..models import Submission, SubmissionVersion
from ..serializers.submission import SubmissionSerializer, SubmissionCreateSerializer
from ..serializers.version import VersionSerializer
from ..services.upload import handle_upload


class SubmissionListCreateView(SuccessResponseMixin, APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsStudent()]
        return [IsAuthenticated()]

    def get(self, request):
        user = request.user
        if user.role == Role.STUDENT:
            from apps.groups.models import GroupMembership
            membership = GroupMembership.objects.filter(student=user).first()
            if not membership:
                return self.success(data=[])
            qs = Submission.objects.filter(group=membership.group)
        elif user.role == Role.SUPERVISOR:
            qs = Submission.objects.filter(group__supervisor=user)
        elif user.role == Role.DEAN:
            qs = Submission.objects.filter(group__department__faculty=user.faculty)
        else:
            qs = Submission.objects.all()
        qs = qs.select_related('group__supervisor', 'group__department__faculty')
        return self.success(data=SubmissionSerializer(qs, many=True).data)

    def post(self, request):
        serializer = SubmissionCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            submission, version = handle_upload(
                group=data['group_id'],
                student=request.user,
                title=data['title'],
                abstract=data['abstract'],
                keywords=data.get('keywords', ''),
                pdf_file=data['file'],
                code_file=data.get('code_file'),
                request=request,
            )
        except ValueError as e:
            return self.error(message=str(e), status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

        return self.created(
            data={
                'id': str(submission.id),
                'slug': submission.slug,
                'title': submission.title,
                'current_version': {
                    'id': str(version.id),
                    'version_number': version.version_number,
                    'status': version.status,
                    'has_code': version.has_code,
                    'uploaded_at': version.uploaded_at.isoformat(),
                },
            },
            message='Submission received. Plagiarism check queued.',
        )


class SubmissionDetailView(SuccessResponseMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        submission = self._get_submission(request, pk)
        return self.success(data=SubmissionSerializer(submission).data)

    def _get_submission(self, request, pk):
        user = request.user
        qs = Submission.objects.select_related('group__supervisor', 'group__department__faculty')
        if user.role == Role.STUDENT:
            from apps.groups.models import GroupMembership
            memberships = GroupMembership.objects.filter(student=user).values_list('group_id', flat=True)
            return get_object_or_404(qs, pk=pk, group__in=memberships)
        elif user.role == Role.SUPERVISOR:
            return get_object_or_404(qs, pk=pk, group__supervisor=user)
        elif user.role == Role.DEAN:
            return get_object_or_404(qs, pk=pk, group__department__faculty=user.faculty)
        return get_object_or_404(qs, pk=pk)


class SubmissionVersionListView(SuccessResponseMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        submission = get_object_or_404(Submission, pk=pk)
        versions = SubmissionVersion.objects.filter(submission=submission).order_by('-version_number')
        return self.success(data=VersionSerializer(versions, many=True).data)
