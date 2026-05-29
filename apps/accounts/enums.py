from django.db import models


class Role(models.TextChoices):
    ADMIN = 'ADMIN', 'System Administrator'
    DEAN = 'DEAN', 'Dean of Faculty'
    SUPERVISOR = 'SUPERVISOR', 'Project Supervisor'
    STUDENT = 'STUDENT', 'Student'
