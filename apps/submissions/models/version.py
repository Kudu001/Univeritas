import uuid
from django.db import models

from apps.submissions.enums import SubmissionStatus


class SubmissionVersion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.ForeignKey(
        'submissions.Submission',
        on_delete=models.CASCADE,
        related_name='versions',
    )
    version_number = models.PositiveIntegerField()
    file = models.FileField(upload_to='dissertations/')
    code_file = models.FileField(upload_to='code/', null=True, blank=True)
    has_code = models.BooleanField(default=False)
    extracted_text = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_versions',
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=30,
        choices=SubmissionStatus.choices,
        default=SubmissionStatus.UPLOADED,
        db_index=True,
    )
    is_current = models.BooleanField(default=True, db_index=True)

    class Meta:
        app_label = 'submissions'
        unique_together = ('submission', 'version_number')
        ordering = ('-version_number',)

    def __str__(self):
        return f'{self.submission.title} v{self.version_number}'
