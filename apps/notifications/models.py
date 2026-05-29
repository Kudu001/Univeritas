import uuid
from django.db import models

from .enums import NotificationType, NotificationChannel


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    type = models.CharField(max_length=50, choices=NotificationType.choices)
    channel = models.CharField(max_length=10, choices=NotificationChannel.choices)
    title = models.CharField(max_length=300)
    body = models.TextField()
    read = models.BooleanField(default=False, db_index=True)
    email_status = models.CharField(max_length=20, null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'notifications'
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.type} → {self.recipient.email}'
