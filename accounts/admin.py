"""
Django admin configuration for custom User model.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for custom User model with role field."""

    # Add 'role' to the fields shown in the admin list view
    list_display = ['username', 'email', 'role', 'first_name', 'is_active']
    list_filter = ['role', 'is_active', 'is_staff']

    # Add 'role' to the edit form fieldsets
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role', {'fields': ('role',)}),
    )

    # Add 'role' to the create user form
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role', {'fields': ('role',)}),
    )
