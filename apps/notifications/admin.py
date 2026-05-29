from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'type', 'channel', 'read', 'email_status', 'created_at')
    list_filter = ('type', 'channel', 'read', 'email_status')
