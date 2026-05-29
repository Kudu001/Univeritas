from rest_framework import serializers
from ..models import PlagiarismMatch, PlagiarismChunkMatch


class PlagiarismMatchSerializer(serializers.ModelSerializer):
    matched_dissertation = serializers.SerializerMethodField()

    class Meta:
        model = PlagiarismMatch
        fields = ('id', 'similarity_score', 'total_chunks_matched', 'matched_dissertation')

    def get_matched_dissertation(self, obj):
        version = obj.matched_version
        submission = version.submission
        return {
            'title': submission.title,
            'academic_year': submission.academic_year,
            'authors': submission.authors,
            'faculty': submission.group.department.faculty.name,
        }


class ChunkMatchSerializer(serializers.ModelSerializer):
    source_chunk = serializers.SerializerMethodField()
    matched_chunk = serializers.SerializerMethodField()

    class Meta:
        model = PlagiarismChunkMatch
        fields = ('similarity_score', 'source_chunk', 'matched_chunk')

    def _chunk_data(self, chunk):
        return {
            'page_number': chunk.page_number,
            'chunk_index': chunk.chunk_index,
            'chunk_type': chunk.chunk_type,
            'content': chunk.content,
        }

    def get_source_chunk(self, obj):
        return self._chunk_data(obj.source_chunk)

    def get_matched_chunk(self, obj):
        return self._chunk_data(obj.matched_chunk)
