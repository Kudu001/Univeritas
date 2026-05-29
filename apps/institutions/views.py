from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from apps.common.mixins import SuccessResponseMixin
from apps.accounts.permissions import IsAdmin
from apps.audit.services import log
from apps.audit.enums import AuditAction
from .models import Faculty, Department
from .serializers import FacultySerializer, DepartmentSerializer


class FacultyListCreateView(SuccessResponseMixin, APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdmin()]
        return [IsAuthenticated()]

    def get(self, request):
        faculties = Faculty.objects.all().order_by('name')
        return self.success(data=FacultySerializer(faculties, many=True).data)

    def post(self, request):
        serializer = FacultySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        faculty = serializer.save()
        log(request.user, AuditAction.FACULTY_CREATED, faculty, request=request)
        return self.created(data=serializer.data, message='Faculty created successfully.')


class FacultyDetailView(SuccessResponseMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        faculty = get_object_or_404(Faculty, pk=pk)
        return self.success(data=FacultySerializer(faculty).data)


class DepartmentListView(SuccessResponseMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, faculty_pk):
        faculty = get_object_or_404(Faculty, pk=faculty_pk)
        departments = faculty.departments.all().order_by('name')
        return self.success(data=DepartmentSerializer(departments, many=True).data)


class DepartmentCreateView(SuccessResponseMixin, APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        serializer = DepartmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dept = serializer.save()
        log(request.user, AuditAction.DEPARTMENT_CREATED, dept, request=request)
        return self.created(data=DepartmentSerializer(dept).data, message='Department created successfully.')


class DepartmentDetailView(SuccessResponseMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        dept = get_object_or_404(Department, pk=pk)
        return self.success(data=DepartmentSerializer(dept).data)
