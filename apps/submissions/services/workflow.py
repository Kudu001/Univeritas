from django.db import transaction
from rest_framework import status as http_status

from apps.audit.services import log
from apps.audit.enums import AuditAction
from apps.notifications.services import notify, notify_group
from apps.notifications.enums import NotificationType
from apps.submissions.models import Submission, SubmissionVersion, SubmissionComment
from apps.submissions.enums import SubmissionStatus
from .versioning import get_current_version


def _assert_report_complete(version):
    from apps.plagiarism.models import PlagiarismReport
    from apps.plagiarism.enums import ReportStatus
    try:
        report = version.plagiarism_report
    except PlagiarismReport.DoesNotExist:
        raise ValueError('Plagiarism report is not yet complete. Approval is locked until the report is ready.')
    if report.status != ReportStatus.COMPLETED:
        raise ValueError('Plagiarism report is not yet complete. Approval is locked until the report is ready.')


@transaction.atomic
def supervisor_approve(version, supervisor, request=None):
    _assert_report_complete(version)
    if version.status != SubmissionStatus.PENDING_SUPERVISOR:
        raise ValueError('Submission is not in a state that can be approved.')

    version.status = SubmissionStatus.PENDING_DEAN
    version.save(update_fields=['status'])
    log(
        actor=supervisor, action=AuditAction.SUPERVISOR_APPROVED, obj=version,
        changes={'status': {'before': SubmissionStatus.PENDING_SUPERVISOR, 'after': SubmissionStatus.PENDING_DEAN}},
        request=request,
    )
    notify_group(
        version.submission.group,
        NotificationType.SUBMISSION_APPROVED,
        title='Submission approved by supervisor',
        body=f'Your dissertation has been approved by your supervisor and forwarded to the dean.',
    )


@transaction.atomic
def supervisor_reject(version, supervisor, comment_body, request=None):
    if version.status not in (SubmissionStatus.PENDING_SUPERVISOR,):
        raise ValueError('Submission cannot be rejected in its current state.')

    version.status = SubmissionStatus.SUPERVISOR_REJECTED
    version.save(update_fields=['status'])

    if comment_body:
        SubmissionComment.objects.create(
            version=version, author=supervisor, body=comment_body
        )
        log(actor=supervisor, action=AuditAction.COMMENT_ADDED, obj=version, request=request)

    log(
        actor=supervisor, action=AuditAction.SUPERVISOR_REJECTED, obj=version,
        changes={'status': {'before': SubmissionStatus.PENDING_SUPERVISOR, 'after': SubmissionStatus.SUPERVISOR_REJECTED}},
        request=request,
    )
    notify_group(
        version.submission.group,
        NotificationType.SUBMISSION_REJECTED,
        title='Submission rejected by supervisor',
        body=f'Your dissertation has been rejected. Reason: {comment_body}',
    )


@transaction.atomic
def dean_approve(version, dean, request=None):
    if version.status != SubmissionStatus.PENDING_DEAN:
        raise ValueError('Submission is not awaiting dean approval.')

    version.status = SubmissionStatus.DEAN_APPROVED
    version.save(update_fields=['status'])
    log(
        actor=dean, action=AuditAction.DEAN_APPROVED, obj=version,
        changes={'status': {'before': SubmissionStatus.PENDING_DEAN, 'after': SubmissionStatus.DEAN_APPROVED}},
        request=request,
    )
    notify_group(
        version.submission.group,
        NotificationType.DEAN_APPROVED,
        title='Dissertation approved by dean',
        body='Your dissertation has received final academic approval from the dean.',
    )


@transaction.atomic
def publish_single(submission, dean, request=None):
    version = get_current_version(submission)
    if not version or version.status != SubmissionStatus.DEAN_APPROVED:
        raise ValueError('Only dean-approved dissertations can be published.')

    version.status = SubmissionStatus.PUBLISHED
    version.save(update_fields=['status'])
    log(
        actor=dean, action=AuditAction.DISSERTATION_PUBLISHED, obj=version, request=request,
    )
    notify_group(
        submission.group,
        NotificationType.DISSERTATION_PUBLISHED,
        title='Your dissertation is now public',
        body='Your dissertation has been published to the public archive.',
    )


@transaction.atomic
def publish_bulk(submission_ids=None, publish_all=False, dean=None, request=None):
    from apps.groups.models import ProjectGroup

    if publish_all:
        versions = SubmissionVersion.objects.filter(
            status=SubmissionStatus.DEAN_APPROVED,
            is_current=True,
            submission__group__department__faculty=dean.faculty,
        ).select_related('submission__group')
    else:
        versions = SubmissionVersion.objects.filter(
            submission__id__in=submission_ids,
            status=SubmissionStatus.DEAN_APPROVED,
            is_current=True,
        ).select_related('submission__group')

    count = 0
    for version in versions:
        publish_single(version.submission, dean, request)
        count += 1
    return count


@transaction.atomic
def revoke(submission, dean, reason, request=None):
    version = get_current_version(submission)
    if not version or version.status != SubmissionStatus.PUBLISHED:
        raise ValueError('Only published dissertations can be revoked.')

    version.status = SubmissionStatus.DEAN_REVOKED
    version.save(update_fields=['status'])
    log(
        actor=dean, action=AuditAction.DISSERTATION_REVOKED, obj=version,
        changes={'reason': reason}, request=request,
    )
    notify_group(
        submission.group,
        NotificationType.DISSERTATION_REVOKED,
        title='Your dissertation has been removed from the archive',
        body=f'Your dissertation has been revoked. Reason: {reason}',
    )


@transaction.atomic
def reprocess(version, admin, request=None):
    from apps.plagiarism.models import PlagiarismReport
    from apps.plagiarism.enums import ReportStatus

    if version.status != SubmissionStatus.PROCESSING_FAILED:
        raise ValueError('Only PROCESSING_FAILED submissions can be reprocessed.')

    version.status = SubmissionStatus.UPLOADED
    version.save(update_fields=['status'])

    try:
        report = version.plagiarism_report
        report.status = ReportStatus.PENDING
        report.save(update_fields=['status'])
    except PlagiarismReport.DoesNotExist:
        pass

    log(actor=admin, action=AuditAction.REPROCESS_TRIGGERED, obj=version, request=request)

    from apps.submissions.tasks import trigger_plagiarism_check
    trigger_plagiarism_check.delay(str(version.id))
