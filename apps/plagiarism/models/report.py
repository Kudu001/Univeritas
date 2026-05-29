import uuid
from django.db import models

from apps.plagiarism.enums import ReportStatus


class PlagiarismReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    version = models.OneToOneField(
        'submissions.SubmissionVersion',
        on_delete=models.CASCADE,
        related_name='plagiarism_report',
    )
    overall_score = models.FloatField(null=True, blank=True)
    status = models.CharField(
        max_length=15,
        choices=ReportStatus.choices,
        default=ReportStatus.PENDING,
    )
    flagged = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'plagiarism'

    def __str__(self):
        return f'Report for {self.version} — {self.status}'
