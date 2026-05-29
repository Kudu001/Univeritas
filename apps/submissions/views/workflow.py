from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404

from apps.common.mixins import SuccessResponseMixin
from apps.accounts.permissions import IsStudent, IsSupervisor, IsDean, IsAdmin
from apps.accounts.enums import Role
from ..models import Submission, SubmissionVersion, SubmissionComment
from ..serializers.comment import CommentSerializer, CommentCreateSerializer
from ..services import workflow as wf
from ..services.versioning import get_current_version
from ..services.upload import handle_upload
from ..enums import SubmissionStatus


def _get_submission_for_supervisor(pk, supervisor):
    return get_object_or_404(Submission, pk=pk, group__supervisor=supervisor)


def _get_submission_for_dean(pk, dean):
    return get_object_or_404(Submission, pk=pk, group__department__faculty=dean.faculty)


class ResubmitView(SuccessResponseMixin, APIView):
    permission_classes = [IsStudent]

    def post(self, request, pk):
        from apps.groups.models import GroupMembership
        submission = get_object_or_404(Submission, pk=pk)
        if not GroupMembership.objects.filter(group=submission.group, student=request.user).exists():
            return self.error(message='Not found.', status_code=status.HTTP_404_NOT_FOUND)

        current = get_current_version(submission)
        if not current or current.status != SubmissionStatus.SUPERVISOR_REJECTED:
            return self.error(
                message='Resubmission is only allowed after a supervisor rejection.',
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        pdf_file = request.FILES.get('file')
        if not pdf_file:
            return self.error(message='PDF file is required.')

        code_file = request.FILES.get('code_file')
        submission_obj, version = handle_upload(
            group=submission.group,
            student=request.user,
            title=submission.title,
            abstract=submission.abstract,
            keywords=submission.keywords,
            pdf_file=pdf_file,
            code_file=code_file,
            request=request,
        )
        return self.created(
            data={
                'id': str(submission_obj.id),
                'version_number': version.version_number,
                'status': version.status,
            },
            message='Resubmission received. Plagiarism check queued.',
        )


class ApproveView(SuccessResponseMixin, APIView):
    permission_classes = [IsSupervisor]

    def post(self, request, pk):
        submission = _get_submission_for_supervisor(pk, request.user)
        version = get_current_version(submission)
        try:
            wf.supervisor_approve(version, request.user, request)
        except ValueError as e:
            return self.error(message=str(e), status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
        return self.success(data={'status': version.status}, message='Submission approved and forwarded to the dean.')


class RejectView(SuccessResponseMixin, APIView):
    permission_classes = [IsSupervisor]

    def post(self, request, pk):
        submission = _get_submission_for_supervisor(pk, request.user)
        version = get_current_version(submission)
        comment_body = request.data.get('comments', '')
        try:
            wf.supervisor_reject(version, request.user, comment_body, request)
        except ValueError as e:
            return self.error(message=str(e), status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
        return self.success(data={'status': version.status}, message='Submission rejected.')


class DeanApproveView(SuccessResponseMixin, APIView):
    permission_classes = [IsDean]

    def post(self, request, pk):
        submission = _get_submission_for_dean(pk, request.user)
        version = get_current_version(submission)
        try:
            wf.dean_approve(version, request.user, request)
        except ValueError as e:
            return self.error(message=str(e), status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
        return self.success(data={'status': version.status}, message='Dissertation approved.')


class PublishView(SuccessResponseMixin, APIView):
    permission_classes = [IsDean]

    def post(self, request, pk):
        submission = _get_submission_for_dean(pk, request.user)
        try:
            wf.publish_single(submission, request.user, request)
        except ValueError as e:
            return self.error(message=str(e), status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
        return self.success(message='Dissertation published to the archive.')


class PublishBulkView(SuccessResponseMixin, APIView):
    permission_classes = [IsDean]

    def post(self, request):
        publish_all = request.data.get('publish_all', False)
        ids = request.data.get('ids', [])
        try:
            count = wf.publish_bulk(
                submission_ids=ids if not publish_all else None,
                publish_all=publish_all,
                dean=request.user,
                request=request,
            )
        except ValueError as e:
            return self.error(message=str(e), status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
        return self.success(data={'published_count': count}, message=f'{count} dissertations published to the archive.')


class RevokeView(SuccessResponseMixin, APIView):
    permission_classes = [IsDean]

    def post(self, request, pk):
        submission = _get_submission_for_dean(pk, request.user)
        reason = request.data.get('reason', '')
        if not reason:
            return self.error(message='A reason is required to revoke a dissertation.')
        try:
            wf.revoke(submission, request.user, reason, request)
        except ValueError as e:
            return self.error(message=str(e), status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
        return self.success(data={'status': SubmissionStatus.DEAN_REVOKED}, message='Dissertation removed from archive. Students notified.')


class ReprocessView(SuccessResponseMixin, APIView):
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        submission = get_object_or_404(Submission, pk=pk)
        version = get_current_version(submission)
        try:
            wf.reprocess(version, request.user, request)
        except ValueError as e:
            return self.error(message=str(e), status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
        return self.success(data={'status': 'PROCESSING'}, message='Plagiarism check re-queued successfully.')


class CommentListCreateView(SuccessResponseMixin, APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsSupervisor()]
        return []

    def _get_version(self, request, pk):
        from apps.accounts.enums import Role as R
        submission = get_object_or_404(Submission, pk=pk)
        user = request.user
        if user.is_authenticated:
            if user.role == R.SUPERVISOR and submission.group.supervisor != user:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied
        version = get_current_version(submission)
        if not version:
            from django.http import Http404
            raise Http404
        return version

    def get(self, request, pk):
        from rest_framework.permissions import IsAuthenticated
        if not request.user.is_authenticated:
            from rest_framework.exceptions import NotAuthenticated
            raise NotAuthenticated
        version = self._get_version(request, pk)
        comments = version.comments.select_related('author')
        return self.success(data=CommentSerializer(comments, many=True).data)

    def post(self, request, pk):
        submission = get_object_or_404(Submission, pk=pk, group__supervisor=request.user)
        version = get_current_version(submission)
        serializer = CommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = SubmissionComment.objects.create(
            version=version, author=request.user, body=serializer.validated_data['body']
        )
        from apps.audit.services import log
        from apps.audit.enums import AuditAction
        log(request.user, AuditAction.COMMENT_ADDED, comment, request=request)
        return self.created(data=CommentSerializer(comment).data)


class CommentResolveView(SuccessResponseMixin, APIView):
    permission_classes = [IsSupervisor]

    def patch(self, request, pk, comment_id):
        submission = get_object_or_404(Submission, pk=pk, group__supervisor=request.user)
        comment = get_object_or_404(SubmissionComment, pk=comment_id, version__submission=submission)
        comment.resolved = True
        comment.save(update_fields=['resolved'])
        from apps.audit.services import log
        from apps.audit.enums import AuditAction
        log(request.user, AuditAction.COMMENT_RESOLVED, comment, request=request)
        return self.success(message='Comment marked as resolved.')
