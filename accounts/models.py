"""
Custom User model for the Resume Bank Management System.

We extend Django's built-in AbstractUser to add a 'role' field,
which helps us distinguish between 'student' and 'admin' (TPO) users.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model with role-based access control.
    
    Roles:
        - 'student': Regular student who can manage profile and apply to drives
        - 'admin': TPO administrator who manages students, analytics, and drives
    """
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('admin', 'Admin'),
    ]
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='student',
        help_text="User role: 'student' or 'admin'"
    )

    @property
    def is_admin(self):
        """Check if user is a TPO admin."""
        return self.role == 'admin'

    @property
    def is_student(self):
        """Check if user is a student."""
        return self.role == 'student'

    def __str__(self):
        return f"{self.email} ({self.role})"
