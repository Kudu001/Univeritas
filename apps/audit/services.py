from django.contrib.contenttypes.models import ContentType

from .models import AuditLog


def log(actor, action, obj, changes=None, request=None):
    ip = _get_ip(request) if request else None
    AuditLog.objects.create(
        actor=actor,
        action=action,
        content_type=ContentType.objects.get_for_model(obj) if obj else None,
        object_id=obj.pk if obj else None,
        object_repr=str(obj) if obj else '',
        changes=changes or {},
        ip_address=ip,
    )


def _get_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')
