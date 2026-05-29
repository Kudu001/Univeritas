import uuid
from django.db import models
from pgvector.django import VectorField

from apps.plagiarism.enums import ChunkType


class DissertationChunk(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    version = models.ForeignKey(
        'submissions.SubmissionVersion',
        on_delete=models.CASCADE,
        related_name='chunks',
    )
    chunk_type = models.CharField(max_length=10, choices=ChunkType.choices, db_index=True)
    chunk_index = models.PositiveIntegerField()
    page_number = models.PositiveIntegerField(null=True, blank=True)
    source_file = models.CharField(max_length=500, null=True, blank=True)
    language = models.CharField(max_length=50, null=True, blank=True)
    content = models.TextField()

    # Text embedding: all-MiniLM-L6-v2 → 384 dimensions
    embedding = VectorField(dimensions=384, null=True, blank=True)

    # Code embedding: CodeBERT → 768 dimensions
    code_embedding = VectorField(dimensions=768, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'plagiarism'

    def __str__(self):
        return f'Chunk {self.chunk_index} ({self.chunk_type}) of {self.version}'
