import uuid
from django.db import models


class PlagiarismMatch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(
        'plagiarism.PlagiarismReport',
        on_delete=models.CASCADE,
        related_name='matches',
    )
    matched_version = models.ForeignKey(
        'submissions.SubmissionVersion',
        on_delete=models.PROTECT,
        related_name='matched_in',
    )
    similarity_score = models.FloatField()
    total_chunks_matched = models.PositiveIntegerField(default=0)

    class Meta:
        app_label = 'plagiarism'
        ordering = ('-similarity_score',)

    def __str__(self):
        return f'Match {self.similarity_score:.2f} → {self.matched_version}'
