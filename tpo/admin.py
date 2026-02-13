"""
Django admin configuration for TPO models.
"""
from django.contrib import admin
from .models import Drive, Application


@admin.register(Drive)
class DriveAdmin(admin.ModelAdmin):
    """Admin interface for Placement Drives."""
    list_display = ['company_name', 'role', 'package', 'status', 'deadline', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['company_name', 'role']


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    """Admin interface for Drive Applications."""
    list_display = ['student', 'drive', 'status', 'applied_at']
    list_filter = ['status', 'applied_at']
    search_fields = ['student__name', 'drive__company_name']
