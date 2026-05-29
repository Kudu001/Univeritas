from django.db import models


class ReportStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    PROCESSING = 'PROCESSING', 'Processing'
    COMPLETED = 'COMPLETED', 'Completed'
    FAILED = 'FAILED', 'Failed'


class ChunkType(models.TextChoices):
    TEXT = 'TEXT', 'Text Chunk'
    CODE = 'CODE', 'Code Chunk'
