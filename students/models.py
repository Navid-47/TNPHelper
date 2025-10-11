"""
Student models for Resume Bank Management System.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import os

def student_resume_path(instance, filename):
    """Generate file path for student resume uploads."""
    # Get file extension
    ext = filename.split('.')[-1]
    # Create new filename: roll_no_resume.pdf
    new_filename = f"{instance.roll_no}_resume.{ext}"
    return os.path.join('resumes', new_filename)

class Student(models.Model):
    """
    Student model to store student information and resume.
    """
    # User account (for login)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    
    # Basic Information
    name = models.CharField(max_length=100, help_text="Full name of the student")
    roll_no = models.CharField(max_length=20, unique=True, help_text="University roll number")
    email = models.EmailField(unique=True, help_text="Student email address")
    
    # Academic Information
    BRANCH_CHOICES = [
        ('CSE', 'Computer Science Engineering'),
        ('ECE', 'Electronics & Communication Engineering'),
        ('EEE', 'Electrical & Electronics Engineering'),
        ('ME', 'Mechanical Engineering'),
        ('CE', 'Civil Engineering'),
        ('IT', 'Information Technology'),
        ('AI', 'Artificial Intelligence'),
        ('DS', 'Data Science'),
    ]
    branch = models.CharField(max_length=10, choices=BRANCH_CHOICES, help_text="Student's branch")
    
    # CGPA with validation (0.0 to 10.0)
    cgpa = models.DecimalField(
        max_digits=3, 
        decimal_places=2,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        help_text="CGPA (0.0 to 10.0)"
    )
    
    # Skills (comma-separated)
    skills = models.TextField(help_text="Skills (comma-separated)")
    
    # Resume file
    resume = models.FileField(
        upload_to=student_resume_path,
        help_text="Upload resume in PDF format (max 10MB)"
    )
    
    # Placement Status
    PLACEMENT_STATUS_CHOICES = [
        ('placed', 'Placed'),
        ('not_placed', 'Not Placed'),
        ('in_process', 'In Process'),
    ]
    placement_status = models.CharField(
        max_length=20,
        choices=PLACEMENT_STATUS_CHOICES,
        default='not_placed',
        help_text="Current placement status"
    )
    
    # Company details (if placed)
    company_name = models.CharField(max_length=100, blank=True, null=True, help_text="Company name (if placed)")
    package = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Package in LPA")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Student"
        verbose_name_plural = "Students"
    
    def __str__(self):
        return f"{self.name} ({self.roll_no})"
    
    def get_skills_list(self):
        """Return skills as a list."""
        if self.skills:
            return [skill.strip() for skill in self.skills.split(',') if skill.strip()]
        return []
    
    def get_branch_display_name(self):
        """Get full branch name."""
        return dict(self.BRANCH_CHOICES).get(self.branch, self.branch)
    
    def is_placed(self):
        """Check if student is placed."""
        return self.placement_status == 'placed'
    
    def get_resume_filename(self):
        """Get just the filename of the resume."""
        if self.resume:
            return os.path.basename(self.resume.name)
        return None 