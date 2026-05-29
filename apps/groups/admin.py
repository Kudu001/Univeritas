from django.contrib import admin
from .models import ProjectGroup, GroupMembership


@admin.register(ProjectGroup)
class ProjectGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'supervisor', 'department', 'academic_year', 'is_active')
    list_filter = ('is_active', 'department__faculty')


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ('student', 'group', 'joined_at')
