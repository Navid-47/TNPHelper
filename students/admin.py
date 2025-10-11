"""
Django admin configuration for Student model.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """
    Admin interface for Student model.
    """
    list_display = [
        'name', 'roll_no', 'email', 'branch', 'cgpa', 
        'placement_status', 'company_name', 'created_at'
    ]
    list_filter = [
        'branch', 'placement_status', 'created_at', 'updated_at'
    ]
    search_fields = ['name', 'roll_no', 'email', 'skills']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'roll_no', 'email')
        }),
        ('Academic Information', {
            'fields': ('branch', 'cgpa', 'skills')
        }),
        ('Resume', {
            'fields': ('resume',)
        }),
        ('Placement Information', {
            'fields': ('placement_status', 'company_name', 'package')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_resume_link(self, obj):
        """Display resume as a download link."""
        if obj.resume:
            return format_html(
                '<a href="{}" target="_blank">Download Resume</a>',
                obj.resume.url
            )
        return "No resume uploaded"
    get_resume_link.short_description = 'Resume'
    
    def get_skills_display(self, obj):
        """Display skills as a list."""
        skills_list = obj.get_skills_list()
        return ', '.join(skills_list) if skills_list else 'No skills listed'
    get_skills_display.short_description = 'Skills'
    
    # Add custom actions
    actions = ['mark_as_placed', 'mark_as_not_placed', 'mark_as_in_process']
    
    def mark_as_placed(self, request, queryset):
        """Mark selected students as placed."""
        updated = queryset.update(placement_status='placed')
        self.message_user(
            request, 
            f'{updated} student(s) marked as placed successfully.'
        )
    mark_as_placed.short_description = "Mark selected students as placed"
    
    def mark_as_not_placed(self, request, queryset):
        """Mark selected students as not placed."""
        updated = queryset.update(placement_status='not_placed')
        self.message_user(
            request, 
            f'{updated} student(s) marked as not placed.'
        )
    mark_as_not_placed.short_description = "Mark selected students as not placed"
    
    def mark_as_in_process(self, request, queryset):
        """Mark selected students as in process."""
        updated = queryset.update(placement_status='in_process')
        self.message_user(
            request, 
            f'{updated} student(s) marked as in process.'
        )
    mark_as_in_process.short_description = "Mark selected students as in process" 