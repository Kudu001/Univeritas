from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404

from apps.common.mixins import SuccessResponseMixin
from apps.accounts.permissions import IsAdmin
from apps.audit.services import log
from apps.audit.enums import AuditAction
from .models import SystemSetting
from .serializers import SystemSettingSerializer


class SystemSettingListView(SuccessResponseMixin, APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        settings = SystemSetting.objects.all().order_by('key')
        serializer = SystemSettingSerializer(settings, many=True)
        return self.success(data=serializer.data)


class SystemSettingDetailView(SuccessResponseMixin, APIView):
    permission_classes = [IsAdmin]

    def get(self, request, key):
        setting = get_object_or_404(SystemSetting, key=key)
        return self.success(data=SystemSettingSerializer(setting).data)

    def patch(self, request, key):
        setting = get_object_or_404(SystemSetting, key=key)
        old_value = setting.value
        serializer = SystemSettingSerializer(setting, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        setting.updated_by = request.user
        serializer.save()
        log(
            actor=request.user,
            action=AuditAction.PROFILE_UPDATED,
            obj=setting,
            changes={'value': {'before': old_value, 'after': setting.value}},
            request=request,
        )
        return self.success(
            data=SystemSettingSerializer(setting).data,
            message='Setting updated successfully.',
        )
