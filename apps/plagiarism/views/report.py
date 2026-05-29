from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from apps.common.mixins import SuccessResponseMixin
from apps.accounts.enums import Role
from apps.submissions.models import SubmissionVersion
from apps.submissions.enums import SubmissionStatus
from ..models import PlagiarismReport
from ..serializers.report import PlagiarismReportSerializer


class PlagiarismReportView(SuccessResponseMixin, APIView):

    def get(self, request, version_id):
        version = get_object_or_404(SubmissionVersion, pk=version_id)
        self._check_access(request.user, version)
        report = get_object_or_404(PlagiarismReport, version=version)
        return self.success(data=PlagiarismReportSerializer(report).data)

    def _check_access(self, user, version):
        from rest_framework.exceptions import PermissionDenied
        role = user.role
        submission = version.submission
        if role == Role.SUPERVISOR:
            if submission.group.supervisor != user:
                raise PermissionDenied
        elif role == Role.DEAN:
            if submission.group.department.faculty != user.faculty:
                raise PermissionDenied
        elif role == Role.STUDENT:
            # Students can only see report after supervisor has made a decision
            from apps.groups.models import GroupMembership
            if not GroupMembership.objects.filter(group=submission.group, student=user).exists():
                raise PermissionDenied
            if version.status not in (
                SubmissionStatus.PENDING_DEAN, SubmissionStatus.DEAN_APPROVED,
                SubmissionStatus.PUBLISHED, SubmissionStatus.SUPERVISOR_REJECTED
            ):
                raise PermissionDenied
        elif role != Role.ADMIN:
            raise PermissionDenied
