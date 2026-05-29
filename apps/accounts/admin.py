from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'full_name', 'role', 'faculty', 'is_active', 'created_at')
    list_filter = ('role', 'faculty', 'is_active')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal', {'fields': ('first_name', 'last_name')}),
        ('Role & Scope', {'fields': ('role', 'faculty', 'password_changed')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'faculty', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'first_name', 'last_name')
