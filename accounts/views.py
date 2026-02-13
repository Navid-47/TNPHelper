"""
Views for user authentication — login, register, and logout.
All auth-related views are centralized here in the accounts app.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.db import transaction
from students.models import Student
from .forms import StudentRegistrationForm, StudentLoginForm, TPOLoginForm


def student_register(request):
    """Handle student registration — creates User + Student profile."""
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    messages.success(request, 'Registration successful! Please login.')
                    return redirect('accounts:student_login')
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
    else:
        form = StudentRegistrationForm()

    return render(request, 'accounts/student_register.html', {'form': form})


def student_login(request):
    """Handle student login — authenticates and checks role."""
    if request.method == 'POST':
        form = StudentLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Make sure this user is actually a student
                if user.is_student:
                    try:
                        student = user.student_profile
                        login(request, user)
                        messages.success(request, f'Welcome back, {student.name}!')
                        return redirect('students:dashboard')
                    except Student.DoesNotExist:
                        messages.error(request, 'No student profile found for this account.')
                else:
                    messages.error(request, 'This account is not a student account.')
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = StudentLoginForm()

    return render(request, 'accounts/student_login.html', {'form': form})


def student_logout(request):
    """Handle student logout."""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('core:home')


def tpo_login(request):
    """Handle TPO admin login — authenticates and checks admin role."""
    if request.method == 'POST':
        form = TPOLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None and user.is_admin:
                login(request, user)
                messages.success(request, f'Welcome, {user.get_full_name() or user.username}!')
                return redirect('tpo:dashboard')
            else:
                messages.error(request, 'Invalid credentials or insufficient permissions.')
    else:
        form = TPOLoginForm()

    return render(request, 'accounts/tpo_login.html', {'form': form})


def tpo_logout(request):
    """Handle TPO admin logout."""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('core:home')
