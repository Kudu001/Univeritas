import uuid
from django.db import models
from django.utils.text import slugify


class Submission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.OneToOneField(
        'groups.ProjectGroup',
        on_delete=models.CASCADE,
        related_name='submission',
    )
    title = models.CharField(max_length=500)
    slug = models.SlugField(max_length=600, unique=True)
    abstract = models.TextField()
    keywords = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'submissions'

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(f'{self.title} {self.group.academic_year}')
            slug = base
            n = 1
            while Submission.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{n}'
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def academic_year(self):
        return self.group.academic_year

    @property
    def authors(self):
        from apps.groups.models import GroupMembership
        memberships = GroupMembership.objects.filter(group=self.group).select_related('student')
        return [m.student.full_name for m in memberships]
