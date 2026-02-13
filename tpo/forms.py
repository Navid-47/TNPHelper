"""
Forms for TPO admin portal.
Includes student filtering, placement status updates, and drive management.
(Login form is in accounts/forms.py)
"""
from django import forms
from students.models import Student
from .models import Drive


class StudentFilterForm(forms.Form):
    """Form for filtering students in the TPO dashboard."""

    # Search by name or roll number
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name or roll number'
        })
    )

    # Filter by branch
    branch = forms.ChoiceField(
        choices=[('', 'All Branches')] + Student.BRANCH_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # Filter by CGPA range
    cgpa_min = forms.DecimalField(
        required=False, min_value=0.0, max_value=10.0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 'placeholder': 'Min CGPA', 'step': '0.01'
        })
    )
    cgpa_max = forms.DecimalField(
        required=False, min_value=0.0, max_value=10.0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 'placeholder': 'Max CGPA', 'step': '0.01'
        })
    )

    # Filter by skills
    skills = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by skills (comma-separated)'
        })
    )

    # Filter by placement status
    placement_status = forms.ChoiceField(
        choices=[('', 'All Status')] + Student.PLACEMENT_STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # Sort options
    SORT_CHOICES = [
        ('', 'Default (Newest First)'),
        ('name', 'Name (A-Z)'),
        ('-name', 'Name (Z-A)'),
        ('roll_no', 'Roll Number (Asc)'),
        ('-roll_no', 'Roll Number (Desc)'),
        ('-cgpa', 'CGPA (High to Low)'),
        ('cgpa', 'CGPA (Low to High)'),
        ('-created_at', 'Newest First'),
        ('created_at', 'Oldest First'),
    ]
    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class PlacementStatusUpdateForm(forms.Form):
    """Form for TPO admin to update a student's placement status."""

    placement_status = forms.ChoiceField(
        choices=Student.PLACEMENT_STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    company_name = forms.CharField(
        required=False, max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Company name (if placed)'
        })
    )
    package = forms.DecimalField(
        required=False, max_digits=6, decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 'step': '0.01',
            'placeholder': 'Package in LPA'
        })
    )

    def clean(self):
        """When status is 'placed', company and package are required."""
        cleaned_data = super().clean()
        if cleaned_data.get('placement_status') == 'placed':
            if not cleaned_data.get('company_name'):
                raise forms.ValidationError('Company name is required when status is "Placed".')
            if not cleaned_data.get('package'):
                raise forms.ValidationError('Package is required when status is "Placed".')
        return cleaned_data


class DriveForm(forms.ModelForm):
    """Form to create a new placement drive."""

    class Meta:
        model = Drive
        fields = [
            'company_name', 'role', 'package', 'description',
            'min_cgpa', 'allowed_branches', 'backlogs_criteria', 'deadline'
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Company Name'
            }),
            'role': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Job Role (e.g., Software Engineer)'
            }),
            'package': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01', 'placeholder': 'Package in LPA'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 4, 'placeholder': 'Job description and details'
            }),
            'min_cgpa': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01', 'placeholder': 'Minimum CGPA (default: 0)'
            }),
            'allowed_branches': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., CSE,ECE,IT (leave blank for all branches)'
            }),
            'backlogs_criteria': forms.Select(attrs={'class': 'form-control'}),
            'deadline': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'
            }),
        }


class ApplicationStatusForm(forms.Form):
    """Form to update a student's application status for a drive."""

    status = forms.ChoiceField(
        choices=[
            ('shortlisted', 'Shortlisted'),
            ('rejected', 'Rejected'),
            ('offered', 'Offered'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )