import random
import string
from django.db import transaction

from .models import CustomUser
from .enums import Role


def generate_password(length=12):
    chars = string.ascii_letters + string.digits + '!@#$%'
    return ''.join(random.choices(chars, k=length))


@transaction.atomic
def create_user(role, first_name, last_name, email, faculty=None, created_by=None, request=None):
    from apps.audit.services import log
    from apps.audit.enums import AuditAction

    raw_password = generate_password()
    user = CustomUser(
        email=email,
        first_name=first_name,
        last_name=last_name,
        role=role,
        faculty=faculty,
    )
    user.set_password(raw_password)
    user.save()

    log(
        actor=created_by,
        action=AuditAction.USER_CREATED,
        obj=user,
        changes={'role': role, 'email': email},
        request=request,
    )

    from .tasks import send_credential_email
    send_credential_email.delay(str(user.id), raw_password)

    return user


def deactivate_user(user, actor, request=None):
    from apps.audit.services import log
    from apps.audit.enums import AuditAction

    user.is_active = False
    user.save(update_fields=['is_active'])
    log(actor=actor, action=AuditAction.USER_DEACTIVATED, obj=user, request=request)


def reactivate_user(user, actor, request=None):
    from apps.audit.services import log
    from apps.audit.enums import AuditAction

    user.is_active = True
    user.save(update_fields=['is_active'])
    log(actor=actor, action=AuditAction.USER_CREATED, obj=user,
        changes={'reactivated': True}, request=request)
