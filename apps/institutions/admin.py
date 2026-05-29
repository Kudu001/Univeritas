from django.contrib import admin
from .models import Faculty, Department


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'created_at')


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'faculty', 'created_at')
    list_filter = ('faculty',)
