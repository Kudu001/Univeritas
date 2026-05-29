import uuid
from django.db import models


class Faculty(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'institutions'
        verbose_name_plural = 'faculties'

    def __str__(self):
        return self.name


class Department(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='departments')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'institutions'
        unique_together = ('code', 'faculty')

    def __str__(self):
        return f'{self.name} ({self.faculty.code})'
