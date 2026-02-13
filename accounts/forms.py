"""
Forms for user authentication — registration and login.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import User
from students.models import Student


class StudentRegistrationForm(UserCreationForm):
    """
    Registration form for new students.
    Creates both a User account (with role='student') and a Student profile.
    """
    # We use email as the username
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        }),
        help_text='This will be your login email'
    )

    # Student profile fields
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your full name'
        })
    )
    roll_no = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your roll number (e.g., CSE2021001)'
        })
    )
    branch = forms.ChoiceField(
        choices=Student.BRANCH_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    cgpa = forms.DecimalField(
        max_digits=4,
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
            'placeholder': 'Enter skills separated by commas (e.g., Python, Java, ML)'
        }),
        help_text='Comma-separated list of skills'
    )

    class Meta:
        model = User
        fields = ('username', 'name', 'roll_no', 'branch', 'cgpa', 'skills',
                  'password1', 'password2')

    def clean_username(self):
        """Make sure email is unique."""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('A user with this email already exists.')
        return username

    def clean_roll_no(self):
        """Make sure roll number is unique."""
        roll_no = self.cleaned_data.get('roll_no')
        if Student.objects.filter(roll_no=roll_no).exists():
            raise ValidationError('A student with this roll number already exists.')
        return roll_no

    def save(self, commit=True):
        """Create User and Student profile together."""
        user = super().save(commit=False)
        user.email = self.cleaned_data['username']
        user.first_name = self.cleaned_data['name']
        user.role = 'student'  # Set role to student

        if commit:
            user.save()
            # Create the student profile linked to this user
            Student.objects.create(
                user=user,
                name=self.cleaned_data['name'],
                roll_no=self.cleaned_data['roll_no'],
                email=self.cleaned_data['username'],
                branch=self.cleaned_data['branch'],
                cgpa=self.cleaned_data['cgpa'],
                skills=self.cleaned_data['skills'],
            )
        return user


class StudentLoginForm(forms.Form):
    """Simple email + password login form for students."""
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


class TPOLoginForm(forms.Form):
    """Login form for TPO administrators."""
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
