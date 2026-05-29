from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task(bind=True, max_retries=3)
def send_credential_email(self, user_id, raw_password):
    from .models import CustomUser
    try:
        user = CustomUser.objects.get(id=user_id)
        subject = 'Your Univeritas Account Credentials'
        body = (
            f'Hello {user.first_name},\n\n'
            f'Your Univeritas account has been created.\n\n'
            f'Login URL: {settings.FRONTEND_URL}/login\n'
            f'Email: {user.email}\n'
            f'Password: {raw_password}\n\n'
            f'Please log in and change your password immediately.\n\n'
            f'Univeritas System'
        )
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [user.email])
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
