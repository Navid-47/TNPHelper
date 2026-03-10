"""
Student model for Resume Bank Management System.
Stores student profile information, academic details, and resume.
"""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
import os


def student_resume_path(instance, filename):
    """
    Generate file path for student resume uploads.
    Files are stored as: media/resumes/{roll_no}_resume.pdf
    """
    ext = filename.split('.')[-1]
    new_filename = f"{instance.roll_no}_resume.{ext}"
    return os.path.join('resumes', new_filename)


class Student(models.Model):
    """
    Student profile model.

    Each student has a one-to-one link to a User account (for login)
    and stores their academic info, skills, resume, and placement status.
    """

    # ── Link to User account ──
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )

    # ── Basic Information ──
    name = models.CharField(max_length=100, help_text="Full name of the student")
    roll_no = models.CharField(max_length=20, unique=True, help_text="University roll number")
    email = models.EmailField(help_text="Student email address")

    # ── Academic Information ──
    BRANCH_CHOICES = [
        ('CSE', 'Computer Science Engineering'),
        ('ECE', 'Electronics & Communication Engineering'),
        ('EEE', 'Electrical & Electronics Engineering'),
        ('ME', 'Mechanical Engineering'),
        ('CE', 'Civil Engineering'),
        ('IT', 'Information Technology'),
        ('AI&DS', 'Artificial Intelligence & Data Science'),
    ]
    branch = models.CharField(max_length=10, choices=BRANCH_CHOICES, help_text="Student's branch")

    # CGPA with validation (0.00 to 10.00)
    cgpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        help_text="CGPA (0.0 to 10.0)"
    )

    # Skills (comma-separated text)
    skills = models.TextField(help_text="Skills (comma-separated)")

    # Resume file (optional — student can upload later)
    resume = models.FileField(
        upload_to=student_resume_path,
        blank=True,
        null=True,
        help_text="Upload resume in PDF format (max 10MB)"
    )

    # ── Placement Status ──
    PLACEMENT_STATUS_CHOICES = [
        ('not_placed', 'Not Placed'),
        ('in_process', 'In Process'),
        ('placed', 'Placed'),
    ]
    placement_status = models.CharField(
        max_length=15,
        choices=PLACEMENT_STATUS_CHOICES,
        default='not_placed',
        help_text="Current placement status"
    )

    # Company details (filled when placed)
    company_name = models.CharField(max_length=100, blank=True, null=True, help_text="Company name (if placed)")
    package = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, help_text="Package in LPA")

    # ── Timestamps ──
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

    def get_profile_completion(self):
        """Calculate profile completion percentage and list missing items."""
        fields = [
            (bool(self.name), 'Full Name'),
            (bool(self.email), 'Email'),
            (bool(self.roll_no), 'Roll Number'),
            (bool(self.branch), 'Branch'),
            (self.cgpa is not None and self.cgpa > 0, 'CGPA'),
            (bool(self.skills and self.skills.strip()), 'Skills'),
            (bool(self.resume), 'Resume'),
        ]
        completed = sum(1 for done, _ in fields if done)
        missing = [name for done, name in fields if not done]
        percentage = round(completed / len(fields) * 100)
        return {'percentage': percentage, 'missing': missing, 'completed': completed, 'total': len(fields)}