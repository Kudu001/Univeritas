import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

from .enums import Role


class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    username = None
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    role = models.CharField(max_length=20, choices=Role.choices)
    faculty = models.ForeignKey(
        'institutions.Faculty',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
    )
    password_changed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        app_label = 'accounts'

    def __str__(self):
        return f'{self.get_full_name()} <{self.email}>'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()
