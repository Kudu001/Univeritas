from .models import Notification
from .enums import NotificationChannel


def notify(recipient, notification_type, title, body, channel=None):
    if channel is None:
        from .enums import NotificationType
        _channel_map = {
            NotificationType.ACCOUNT_CREATED: NotificationChannel.EMAIL,
            NotificationType.SUBMISSION_RECEIVED: NotificationChannel.IN_APP,
            NotificationType.PLAGIARISM_REPORT_READY: NotificationChannel.IN_APP,
            NotificationType.SUBMISSION_APPROVED: NotificationChannel.BOTH,
            NotificationType.SUBMISSION_REJECTED: NotificationChannel.BOTH,
            NotificationType.DEAN_APPROVED: NotificationChannel.BOTH,
            NotificationType.DISSERTATION_PUBLISHED: NotificationChannel.BOTH,
            NotificationType.DISSERTATION_REVOKED: NotificationChannel.BOTH,
        }
        channel = _channel_map.get(notification_type, NotificationChannel.IN_APP)

    notification = Notification.objects.create(
        recipient=recipient,
        type=notification_type,
        channel=channel,
        title=title,
        body=body,
        email_status='PENDING' if channel in (NotificationChannel.EMAIL, NotificationChannel.BOTH) else None,
    )

    if channel in (NotificationChannel.EMAIL, NotificationChannel.BOTH):
        from .tasks import send_email
        send_email.delay(str(notification.id))

    return notification


def notify_group(group, notification_type, title, body):
    from apps.groups.models import GroupMembership
    members = GroupMembership.objects.filter(group=group).select_related('student')
    for membership in members:
        notify(membership.student, notification_type, title, body)
