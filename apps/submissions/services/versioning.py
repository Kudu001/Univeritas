from apps.submissions.models import Submission, SubmissionVersion


def get_current_version(submission):
    return SubmissionVersion.objects.filter(submission=submission, is_current=True).first()


def get_next_version_number(submission):
    last = SubmissionVersion.objects.filter(submission=submission).order_by('-version_number').first()
    return (last.version_number + 1) if last else 1


def set_current(new_version):
    SubmissionVersion.objects.filter(
        submission=new_version.submission, is_current=True
    ).exclude(pk=new_version.pk).update(is_current=False)
    if not new_version.is_current:
        new_version.is_current = True
        new_version.save(update_fields=['is_current'])
