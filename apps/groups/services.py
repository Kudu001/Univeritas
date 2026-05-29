from django.db import transaction
from django.utils import timezone

from apps.audit.services import log
from apps.audit.enums import AuditAction
from apps.accounts.services import create_user
from apps.accounts.enums import Role
from .models import ProjectGroup, GroupMembership


MAX_GROUP_SIZE = 3


@transaction.atomic
def create_group(supervisor, department, name, academic_year, request=None):
    group = ProjectGroup.objects.create(
        supervisor=supervisor,
        department=department,
        name=name,
        academic_year=academic_year,
    )
    log(actor=supervisor, action=AuditAction.GROUP_CREATED, obj=group, request=request)
    return group


@transaction.atomic
def add_member(group, first_name, last_name, email, supervisor, request=None):
    current_count = GroupMembership.objects.filter(group=group).count()
    if current_count >= MAX_GROUP_SIZE:
        raise ValueError(f'Group already has the maximum of {MAX_GROUP_SIZE} members.')

    student = create_user(
        role=Role.STUDENT,
        first_name=first_name,
        last_name=last_name,
        email=email,
        created_by=supervisor,
        request=request,
    )
    membership = GroupMembership.objects.create(group=group, student=student)
    log(
        actor=supervisor,
        action=AuditAction.STUDENT_ADDED_TO_GROUP,
        obj=membership,
        changes={'group': str(group.id), 'student': email},
        request=request,
    )
    return membership


@transaction.atomic
def remove_member(group, student, supervisor, request=None):
    from apps.submissions.models import Submission
    if Submission.objects.filter(group=group).exists():
        raise ValueError('Cannot remove a student after a submission has been made.')
    GroupMembership.objects.filter(group=group, student=student).delete()


@transaction.atomic
def deactivate_group(group, dean, request=None):
    group.is_active = False
    group.deactivated_by = dean
    group.deactivated_at = timezone.now()
    group.save(update_fields=['is_active', 'deactivated_by', 'deactivated_at'])
    log(actor=dean, action=AuditAction.GROUP_DEACTIVATED, obj=group, request=request)
