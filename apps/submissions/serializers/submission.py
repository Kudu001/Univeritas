from rest_framework import serializers
from ..models import Submission, SubmissionVersion


class VersionBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionVersion
        fields = ('id', 'version_number', 'status', 'has_code', 'uploaded_at')


class SubmissionSerializer(serializers.ModelSerializer):
    academic_year = serializers.CharField(read_only=True)
    authors = serializers.ListField(child=serializers.CharField(), read_only=True)
    faculty = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    supervisor = serializers.SerializerMethodField()
    current_version = serializers.SerializerMethodField()

    class Meta:
        model = Submission
        fields = ('id', 'slug', 'title', 'abstract', 'keywords',
                  'academic_year', 'authors', 'faculty', 'department', 'supervisor',
                  'current_version', 'created_at', 'updated_at')

    def get_faculty(self, obj):
        return {'id': str(obj.group.department.faculty.id), 'name': obj.group.department.faculty.name}

    def get_department(self, obj):
        return {'id': str(obj.group.department.id), 'name': obj.group.department.name}

    def get_supervisor(self, obj):
        return {'id': str(obj.group.supervisor.id), 'full_name': obj.group.supervisor.full_name}

    def get_current_version(self, obj):
        version = SubmissionVersion.objects.filter(submission=obj, is_current=True).first()
        if version:
            return VersionBriefSerializer(version).data
        return None


class SubmissionCreateSerializer(serializers.Serializer):
    group_id = serializers.UUIDField()
    title = serializers.CharField(max_length=500)
    abstract = serializers.CharField()
    keywords = serializers.CharField(required=False, allow_blank=True, default='')
    file = serializers.FileField()
    code_file = serializers.FileField(required=False, allow_null=True)

    def validate_group_id(self, value):
        from apps.groups.models import ProjectGroup, GroupMembership
        student = self.context['request'].user
        try:
            group = ProjectGroup.objects.get(id=value)
        except ProjectGroup.DoesNotExist:
            raise serializers.ValidationError('Group not found.')
        if not GroupMembership.objects.filter(group=group, student=student).exists():
            raise serializers.ValidationError('You are not a member of this group.')
        return group
