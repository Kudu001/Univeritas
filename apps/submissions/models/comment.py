import uuid
from django.db import models


class SubmissionComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    version = models.ForeignKey(
        'submissions.SubmissionVersion',
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='submission_comments',
    )
    body = models.TextField()
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'submissions'
        ordering = ('created_at',)

    def __str__(self):
        return f'Comment on {self.version} by {self.author}'
