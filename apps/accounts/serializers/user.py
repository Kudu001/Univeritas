from rest_framework import serializers
from apps.institutions.serializers import FacultySerializer
from ..models import CustomUser


class UserBriefSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'full_name', 'role')


class ProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    faculty = FacultySerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'first_name', 'last_name', 'full_name',
                  'role', 'faculty', 'password_changed', 'created_at')
        read_only_fields = ('id', 'email', 'role', 'faculty', 'password_changed', 'created_at')


class CreateDeanSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    faculty_id = serializers.UUIDField()

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value

    def validate_faculty_id(self, value):
        from apps.institutions.models import Faculty
        try:
            return Faculty.objects.get(id=value)
        except Faculty.DoesNotExist:
            raise serializers.ValidationError('Faculty not found.')


class CreateSupervisorSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value


class DeanSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    faculty = FacultySerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'full_name', 'role', 'faculty', 'is_active', 'created_at')


class SupervisorSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    faculty = FacultySerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'full_name', 'role', 'faculty', 'is_active', 'created_at')
