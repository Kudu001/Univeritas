from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone


@shared_task(bind=True, max_retries=3)
def send_email(self, notification_id):
    from .models import Notification
    try:
        notification = Notification.objects.select_related('recipient').get(id=notification_id)
        send_mail(
            subject=notification.title,
            message=notification.body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[notification.recipient.email],
        )
        notification.email_status = 'SENT'
        notification.sent_at = timezone.now()
        notification.save(update_fields=['email_status', 'sent_at'])
    except Exception as exc:
        from .models import Notification
        try:
            Notification.objects.filter(id=notification_id).update(email_status='FAILED')
        except Exception:
            pass
        raise self.retry(exc=exc, countdown=120)
