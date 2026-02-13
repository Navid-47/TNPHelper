"""
Models for TPO admin portal.
Contains Drive (placement drives) and Application (student applications).
"""
from django.db import models


class Drive(models.Model):
    """
    Placement Drive model.

    Represents a campus recruitment drive created by the TPO admin.
    Students can apply to active drives if they meet the eligibility criteria.
    """
    company_name = models.CharField(max_length=100, help_text="Name of the recruiting company")
    role = models.CharField(max_length=100, help_text="Job role/position title")
    package = models.DecimalField(max_digits=6, decimal_places=2, help_text="Package offered in LPA")
    description = models.TextField(blank=True, null=True, help_text="Job description and details")

    # Eligibility criteria
    min_cgpa = models.DecimalField(
        max_digits=4, decimal_places=2, default=0.00,
        help_text="Minimum CGPA required"
    )
    allowed_branches = models.CharField(
        max_length=200, blank=True,
        help_text="Comma-separated branch codes (e.g., CSE,ECE,IT). Leave blank for all."
    )

    BACKLOGS_CHOICES = [
        ('any', 'Any'),
        ('no_active', 'No Active Backlogs'),
        ('no_history', 'No Backlog History'),
    ]
    backlogs_criteria = models.CharField(
        max_length=20, choices=BACKLOGS_CHOICES, default='any',
        help_text="Backlogs eligibility requirement"
    )

    deadline = models.DateField(blank=True, null=True, help_text="Application deadline")

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Placement Drive"
        verbose_name_plural = "Placement Drives"

    def __str__(self):
        return f"{self.company_name} - {self.role} ({self.status})"


class Application(models.Model):
    """
    Student application to a placement drive.

    Each student can apply to a drive only once (unique_together constraint).
    The TPO admin can update the application status.
    """
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
        ('offered', 'Offered'),
    ]

    drive = models.ForeignKey(
        Drive, on_delete=models.CASCADE, related_name='applications',
        help_text="The drive being applied to"
    )
    student = models.ForeignKey(
        'students.Student', on_delete=models.CASCADE, related_name='applications',
        help_text="The student applying"
    )
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='applied')

    class Meta:
        # One student can apply to a drive only once
        unique_together = ('drive', 'student')
        ordering = ['-applied_at']
        verbose_name = "Drive Application"
        verbose_name_plural = "Drive Applications"

    def __str__(self):
        return f"{self.student.name} → {self.drive.company_name} ({self.status})"
