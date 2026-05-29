from django.db import models


class NotificationType(models.TextChoices):
    ACCOUNT_CREATED = 'ACCOUNT_CREATED', 'Account Created'
    SUBMISSION_RECEIVED = 'SUBMISSION_RECEIVED', 'Submission Received'
    PLAGIARISM_REPORT_READY = 'PLAGIARISM_REPORT_READY', 'Plagiarism Report Ready'
    SUBMISSION_APPROVED = 'SUBMISSION_APPROVED', 'Submission Approved'
    SUBMISSION_REJECTED = 'SUBMISSION_REJECTED', 'Submission Rejected'
    DEAN_APPROVED = 'DEAN_APPROVED', 'Dean Approved'
    DISSERTATION_PUBLISHED = 'DISSERTATION_PUBLISHED', 'Dissertation Published'
    DISSERTATION_REVOKED = 'DISSERTATION_REVOKED', 'Dissertation Revoked'


class NotificationChannel(models.TextChoices):
    EMAIL = 'EMAIL', 'Email Only'
    IN_APP = 'IN_APP', 'In-App Only'
    BOTH = 'BOTH', 'Email and In-App'
