"""
Forms for student profile management and resume upload.
(Registration and login forms are in accounts/forms.py)
"""
from django import forms
from django.core.exceptions import ValidationError
from .models import Student
import os


class StudentProfileForm(forms.ModelForm):
    """Form for updating student profile information."""

    class Meta:
        model = Student
        fields = ['name', 'branch', 'cgpa', 'skills', 'placement_status', 'company_name', 'package']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'branch': forms.Select(attrs={'class': 'form-control'}),
            'cgpa': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.0',
                'max': '10.0'
            }),
            'skills': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter skills separated by commas'
            }),
            'placement_status': forms.Select(attrs={'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter company name (if placed)'
            }),
            'package': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.0',
                'placeholder': 'Package in LPA'
            }),
        }

    def clean_package(self):
        """Package is required when placed."""
        package = self.cleaned_data.get('package')
        placement_status = self.cleaned_data.get('placement_status')
        if placement_status == 'placed' and not package:
            raise ValidationError('Package is required when placement status is "Placed".')
        return package

    def clean_company_name(self):
        """Company name is required when placed."""
        company_name = self.cleaned_data.get('company_name')
        placement_status = self.cleaned_data.get('placement_status')
        if placement_status == 'placed' and not company_name:
            raise ValidationError('Company name is required when placement status is "Placed".')
        return company_name


class ResumeUploadForm(forms.ModelForm):
    """Form for uploading a PDF resume file."""

    class Meta:
        model = Student
        fields = ['resume']
        widgets = {
            'resume': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf'
            })
        }

    def clean_resume(self):
        """Validate resume — PDF only, max 10MB."""
        resume = self.cleaned_data.get('resume')
        if resume:
            # Check file size (10MB limit)
            if resume.size > 10 * 1024 * 1024:
                raise ValidationError('Resume file size must be less than 10MB.')
            # Check file extension
            ext = os.path.splitext(resume.name)[1].lower()
            if ext != '.pdf':
                raise ValidationError('Only PDF files are allowed.')
        return resume