from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'actor', 'object_repr', 'timestamp')
    list_filter = ('action',)
    readonly_fields = ('id', 'actor', 'action', 'content_type', 'object_id',
                       'object_repr', 'changes', 'ip_address', 'timestamp', 'extra')
    ordering = ('-timestamp',)
