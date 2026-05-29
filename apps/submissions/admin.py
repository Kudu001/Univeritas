from django.contrib import admin
from .models import Submission, SubmissionVersion, SubmissionComment


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('title', 'group', 'created_at')


@admin.register(SubmissionVersion)
class SubmissionVersionAdmin(admin.ModelAdmin):
    list_display = ('submission', 'version_number', 'status', 'is_current', 'uploaded_at')
    list_filter = ('status', 'is_current')


@admin.register(SubmissionComment)
class SubmissionCommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'version', 'resolved', 'created_at')
    list_filter = ('resolved',)
