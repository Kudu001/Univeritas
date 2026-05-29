from rest_framework import serializers
from .models import Faculty, Department


class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = ('id', 'name', 'code', 'created_at')
        read_only_fields = ('id', 'created_at')


class DepartmentSerializer(serializers.ModelSerializer):
    faculty = FacultySerializer(read_only=True)
    faculty_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Department
        fields = ('id', 'name', 'code', 'faculty', 'faculty_id', 'created_at')
        read_only_fields = ('id', 'created_at')

    def create(self, validated_data):
        faculty_id = validated_data.pop('faculty_id')
        from .models import Faculty as FacultyModel
        faculty = FacultyModel.objects.get(id=faculty_id)
        return Department.objects.create(faculty=faculty, **validated_data)


class DepartmentBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ('id', 'name', 'code')
