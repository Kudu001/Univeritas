from django.contrib import admin
from .models import DissertationChunk, PlagiarismReport, PlagiarismMatch, PlagiarismChunkMatch


@admin.register(PlagiarismReport)
class PlagiarismReportAdmin(admin.ModelAdmin):
    list_display = ('version', 'status', 'overall_score', 'flagged', 'completed_at')
    list_filter = ('status', 'flagged')


@admin.register(PlagiarismMatch)
class PlagiarismMatchAdmin(admin.ModelAdmin):
    list_display = ('report', 'matched_version', 'similarity_score', 'total_chunks_matched')


@admin.register(DissertationChunk)
class DissertationChunkAdmin(admin.ModelAdmin):
    list_display = ('version', 'chunk_type', 'chunk_index', 'page_number')
    list_filter = ('chunk_type',)
