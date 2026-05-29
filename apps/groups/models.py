import uuid
from django.db import models


class ProjectGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    supervisor = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.PROTECT,
        related_name='supervised_groups',
    )
    department = models.ForeignKey(
        'institutions.Department',
        on_delete=models.PROTECT,
        related_name='groups',
    )
    academic_year = models.CharField(max_length=9)  # YYYY/YYYY
    is_active = models.BooleanField(default=True)
    deactivated_by = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deactivated_groups',
    )
    deactivated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'groups'

    def __str__(self):
        return f'{self.name} ({self.academic_year})'


class GroupMembership(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(ProjectGroup, on_delete=models.CASCADE, related_name='memberships')
    student = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
        related_name='group_memberships',
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'groups'
        unique_together = ('group', 'student')

    def __str__(self):
        return f'{self.student.email} in {self.group.name}'
