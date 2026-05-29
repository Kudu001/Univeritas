from rest_framework import serializers
from .models import SystemSetting


class SystemSettingSerializer(serializers.ModelSerializer):
    updated_by = serializers.SerializerMethodField()

    class Meta:
        model = SystemSetting
        fields = ('key', 'value', 'description', 'updated_by', 'updated_at')
        read_only_fields = ('key', 'description', 'updated_by', 'updated_at')

    def get_updated_by(self, obj):
        if obj.updated_by:
            return obj.updated_by.email
        return None
