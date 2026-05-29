import uuid
from django.db import models


class PlagiarismChunkMatch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    match = models.ForeignKey(
        'plagiarism.PlagiarismMatch',
        on_delete=models.CASCADE,
        related_name='chunk_matches',
    )
    source_chunk = models.ForeignKey(
        'plagiarism.DissertationChunk',
        on_delete=models.PROTECT,
        related_name='source_matches',
    )
    matched_chunk = models.ForeignKey(
        'plagiarism.DissertationChunk',
        on_delete=models.PROTECT,
        related_name='archive_matches',
    )
    similarity_score = models.FloatField()

    class Meta:
        app_label = 'plagiarism'
        ordering = ('-similarity_score',)

    def __str__(self):
        return f'ChunkMatch {self.similarity_score:.2f}'
