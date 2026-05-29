from django.contrib import admin
from .models import SystemSetting


@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'updated_by', 'updated_at')
    readonly_fields = ('updated_at',)
