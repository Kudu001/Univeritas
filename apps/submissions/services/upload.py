from django.db import transaction

from apps.audit.services import log
from apps.audit.enums import AuditAction
from apps.submissions.models import Submission, SubmissionVersion
from apps.submissions.enums import SubmissionStatus
from .versioning import get_next_version_number, set_current


@transaction.atomic
def handle_upload(group, student, title, abstract, keywords, pdf_file, code_file=None, request=None):
    submission, created = Submission.objects.get_or_create(
        group=group,
        defaults={'title': title, 'abstract': abstract, 'keywords': keywords or ''},
    )

    version_number = get_next_version_number(submission)
    version = SubmissionVersion.objects.create(
        submission=submission,
        version_number=version_number,
        file=pdf_file,
        code_file=code_file,
        has_code=bool(code_file),
        uploaded_by=student,
        status=SubmissionStatus.UPLOADED,
        is_current=True,
    )
    set_current(version)

    action = AuditAction.SUBMISSION_UPLOADED if version_number == 1 else AuditAction.SUBMISSION_RESUBMITTED
    log(actor=student, action=action, obj=version, request=request)

    # Notify supervisor
    from apps.notifications.services import notify
    from apps.notifications.enums import NotificationType
    notify(
        recipient=group.supervisor,
        notification_type=NotificationType.SUBMISSION_RECEIVED,
        title='New dissertation submission',
        body=f'{student.full_name} uploaded a dissertation for group {group.name}.',
    )

    # Queue plagiarism check
    from apps.submissions.tasks import trigger_plagiarism_check
    trigger_plagiarism_check.delay(str(version.id))

    return submission, version
