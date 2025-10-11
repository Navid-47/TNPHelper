"""
Forms for student registration and profile management.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Student
import os

class StudentRegistrationForm(UserCreationForm):
    """
    Form for student registration with additional fields.
    """
    # Override username field to use email
    username = forms.EmailField(
        label='Email',
        help_text='Enter your email address as username'
    )
    
    # Additional fields
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your full name'})
    )
    roll_no = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your roll number'})
    )
    branch = forms.ChoiceField(
        choices=Student.BRANCH_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    cgpa = forms.DecimalField(
        max_digits=3,
        decimal_places=2,
        min_value=0.0,
        max_value=10.0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter CGPA (0.0 to 10.0)',
            'step': '0.01'
        })
    )
    skills = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter your skills (comma-separated)'
        }),
        help_text='Enter skills separated by commas (e.g., Python, Java, Machine Learning)'
    )
    
    class Meta:
        model = User
        fields = ('username', 'name', 'roll_no', 'branch', 'cgpa', 'skills', 'password1', 'password2')
    
    def clean_username(self):
        """Validate that username (email) is unique."""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('A user with this email already exists.')
        return username
    
    def clean_roll_no(self):
        """Validate that roll number is unique."""
        roll_no = self.cleaned_data.get('roll_no')
        if Student.objects.filter(roll_no=roll_no).exists():
            raise ValidationError('A student with this roll number already exists.')
        return roll_no
    
    def save(self, commit=True):
        """Save the user and create student profile."""
        user = super().save(commit=False)
        user.email = self.cleaned_data['username']  # Set email from username
        user.first_name = self.cleaned_data['name']
        
        if commit:
            user.save()
            # Create student profile
            Student.objects.create(
                user=user,
                name=self.cleaned_data['name'],
                roll_no=self.cleaned_data['roll_no'],
                email=self.cleaned_data['username'],
                branch=self.cleaned_data['branch'],
                cgpa=self.cleaned_data['cgpa'],
                skills=self.cleaned_data['skills']
            )
        return user

class StudentProfileForm(forms.ModelForm):
    """
    Form for updating student profile information.
    """
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
        """Validate package if placement status is placed."""
        package = self.cleaned_data.get('package')
        placement_status = self.cleaned_data.get('placement_status')
        
        if placement_status == 'placed' and not package:
            raise ValidationError('Package is required when placement status is "Placed".')
        
        return package
    
    def clean_company_name(self):
        """Validate company name if placement status is placed."""
        company_name = self.cleaned_data.get('company_name')
        placement_status = self.cleaned_data.get('placement_status')
        
        if placement_status == 'placed' and not company_name:
            raise ValidationError('Company name is required when placement status is "Placed".')
        
        return company_name

class ResumeUploadForm(forms.ModelForm):
    """
    Form for uploading resume file.
    """
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
        """Validate resume file."""
        resume = self.cleaned_data.get('resume')
        
        if resume:
            # Check file size (10MB limit)
            if resume.size > 10 * 1024 * 1024:  # 10MB
                raise ValidationError('Resume file size must be less than 10MB.')
            
            # Check file extension
            ext = os.path.splitext(resume.name)[1].lower()
            if ext != '.pdf':
                raise ValidationError('Only PDF files are allowed.')
        
        return resume

class StudentLoginForm(forms.Form):
    """
    Form for student login.
    """
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    ) 