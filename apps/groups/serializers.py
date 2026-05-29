from rest_framework import serializers
from apps.accounts.serializers.user import UserBriefSerializer
from apps.institutions.serializers import DepartmentSerializer, DepartmentBriefSerializer
from .models import ProjectGroup, GroupMembership


class GroupMemberSerializer(serializers.ModelSerializer):
    student = UserBriefSerializer(read_only=True)

    class Meta:
        model = GroupMembership
        fields = ('id', 'student', 'joined_at')


class ProjectGroupSerializer(serializers.ModelSerializer):
    supervisor = UserBriefSerializer(read_only=True)
    department = DepartmentBriefSerializer(read_only=True)
    members = GroupMemberSerializer(source='memberships', many=True, read_only=True)
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = ProjectGroup
        fields = ('id', 'name', 'supervisor', 'department', 'academic_year',
                  'is_active', 'members', 'member_count', 'created_at')

    def get_member_count(self, obj):
        return obj.memberships.count()


class CreateGroupSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    department_id = serializers.UUIDField()
    academic_year = serializers.RegexField(
        r'^\d{4}/\d{4}$',
        error_messages={'invalid': 'Academic year must be in YYYY/YYYY format.'},
    )

    def validate_department_id(self, value):
        from apps.institutions.models import Department
        try:
            dept = Department.objects.select_related('faculty').get(id=value)
        except Department.DoesNotExist:
            raise serializers.ValidationError('Department not found.')
        supervisor = self.context['request'].user
        if dept.faculty != supervisor.faculty:
            raise serializers.ValidationError('Department does not belong to your faculty.')
        return dept


class AddMemberSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()

    def validate_email(self, value):
        from apps.accounts.models import CustomUser
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value
