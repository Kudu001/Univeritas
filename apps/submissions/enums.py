from django.db import models


class SubmissionStatus(models.TextChoices):
    UPLOADED = 'UPLOADED', 'Uploaded'
    PROCESSING = 'PROCESSING', 'Processing'
    PENDING_SUPERVISOR = 'PENDING_SUPERVISOR', 'Pending Supervisor Review'
    SUPERVISOR_REJECTED = 'SUPERVISOR_REJECTED', 'Rejected by Supervisor'
    PENDING_DEAN = 'PENDING_DEAN', 'Pending Dean Approval'
    DEAN_APPROVED = 'DEAN_APPROVED', 'Dean Approved'
    PUBLISHED = 'PUBLISHED', 'Published'
    PROCESSING_FAILED = 'PROCESSING_FAILED', 'Processing Failed'
    DEAN_REVOKED = 'DEAN_REVOKED', 'Revoked by Dean'
