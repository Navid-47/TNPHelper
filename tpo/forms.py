"""
Forms for TPO login and student filtering.
"""
from django import forms
from students.models import Student

class TPOLoginForm(forms.Form):
    """
    Form for TPO login.
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
    )

class StudentFilterForm(forms.Form):
    """
    Form for filtering students in TPO dashboard.
    """
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
        required=False,
        min_value=0.0,
        max_value=10.0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min CGPA',
            'step': '0.01'
        })
    )
    
    cgpa_max = forms.DecimalField(
        required=False,
        min_value=0.0,
        max_value=10.0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max CGPA',
            'step': '0.01'
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
        ('name', 'Name (A-Z)'),
        ('-name', 'Name (Z-A)'),
        ('roll_no', 'Roll Number'),
        ('-cgpa', 'CGPA (High to Low)'),
        ('cgpa', 'CGPA (Low to High)'),
        ('-created_at', 'Newest First'),
        ('created_at', 'Oldest First'),
    ]
    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        initial='-created_at',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class PlacementStatusUpdateForm(forms.Form):
    """
    Form for updating student placement status.
    """
    placement_status = forms.ChoiceField(
        choices=Student.PLACEMENT_STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    company_name = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Company name (if placed)'
        })
    )
    package = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': 'Package in LPA'
        })
    )
    
    def clean(self):
        """Validate form data."""
        cleaned_data = super().clean()
        placement_status = cleaned_data.get('placement_status')
        company_name = cleaned_data.get('company_name')
        package = cleaned_data.get('package')
        
        if placement_status == 'placed':
            if not company_name:
                raise forms.ValidationError('Company name is required when status is "Placed".')
            if not package:
                raise forms.ValidationError('Package is required when status is "Placed".')
        
        return cleaned_data 