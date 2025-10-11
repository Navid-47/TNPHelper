"""
Views for student registration, login, and profile management.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.contrib.auth.models import User
from django.db import transaction
from .models import Student
from .forms import StudentRegistrationForm, StudentProfileForm, ResumeUploadForm, StudentLoginForm
import os

def student_register(request):
    """
    Handle student registration.
    """
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    messages.success(request, 'Registration successful! Please login.')
                    return redirect('students:login')
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
    else:
        form = StudentRegistrationForm()
    
    return render(request, 'students/register.html', {'form': form})

def student_login(request):
    """
    Handle student login.
    """
    if request.method == 'POST':
        form = StudentLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                # Check if user has a student profile
                try:
                    student = user.student_profile
                    login(request, user)
                    messages.success(request, f'Welcome back, {student.name}!')
                    return redirect('students:dashboard')
                except Student.DoesNotExist:
                    messages.error(request, 'No student profile found for this account.')
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = StudentLoginForm()
    
    return render(request, 'students/login.html', {'form': form})

@login_required
def student_dashboard(request):
    """
    Student dashboard showing profile and resume information.
    """
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('students:login')
    
    context = {
        'student': student,
        'skills_list': student.get_skills_list(),
    }
    return render(request, 'students/dashboard.html', context)

@login_required
def student_profile(request):
    """
    Display and edit student profile.
    """
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('students:login')
    
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('students:profile')
    else:
        form = StudentProfileForm(instance=student)
    
    context = {
        'form': form,
        'student': student,
    }
    return render(request, 'students/profile.html', context)

@login_required
def upload_resume(request):
    """
    Handle resume upload.
    """
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('students:login')
    
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            # Delete old resume file if it exists
            if student.resume and os.path.exists(student.resume.path):
                os.remove(student.resume.path)
            
            form.save()
            messages.success(request, 'Resume uploaded successfully!')
            return redirect('students:dashboard')
    else:
        form = ResumeUploadForm(instance=student)
    
    context = {
        'form': form,
        'student': student,
    }
    return render(request, 'students/upload_resume.html', context)

@login_required
def download_resume(request):
    """
    Allow students to download their own resume.
    """
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('students:login')
    
    if not student.resume:
        messages.error(request, 'No resume uploaded yet.')
        return redirect('students:dashboard')
    
    if os.path.exists(student.resume.path):
        with open(student.resume.path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="{student.get_resume_filename()}"'
            return response
    else:
        messages.error(request, 'Resume file not found.')
        return redirect('students:dashboard')

@login_required
def student_logout(request):
    """
    Handle student logout.
    """
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home') 