from rest_framework import serializers
from ..models import SubmissionVersion


class VersionSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.SerializerMethodField()

    class Meta:
        model = SubmissionVersion
        fields = ('id', 'version_number', 'status', 'has_code',
                  'uploaded_by', 'uploaded_by_name', 'uploaded_at', 'is_current')

    def get_uploaded_by_name(self, obj):
        return obj.uploaded_by.full_name if obj.uploaded_by else None


class ResubmitSerializer(serializers.Serializer):
    file = serializers.FileField()
    code_file = serializers.FileField(required=False, allow_null=True)
