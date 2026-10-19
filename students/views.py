"""
Views for the student portal.
Handles dashboard, profile management, resume upload, and placement drives.

All views use @student_required to ensure only students can access them.
(Authentication views are in accounts/views.py)
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, FileResponse
from accounts.decorators import student_required
from .models import Student
from .forms import StudentProfileForm, ResumeUploadForm
from tpo.models import Drive, Application
import os


@student_required
def student_dashboard(request):
    """Student dashboard — shows profile summary, resume status, placement info."""
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('accounts:student_login')

    context = {
        'student': student,
        'skills_list': student.get_skills_list(),
        'profile_completion': student.get_profile_completion(),
    }
    return render(request, 'students/dashboard.html', context)


@student_required
def student_profile(request):
    """View and edit student profile."""
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('accounts:student_login')

    if request.method == 'POST':
        form = StudentProfileForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('students:dashboard')
    else:
        form = StudentProfileForm(instance=student)

    context = {
        'form': form,
        'student': student,
    }
    return render(request, 'students/profile.html', context)


@student_required
def upload_resume(request):
    """Handle resume PDF upload — replaces existing resume only after successful upload."""
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('accounts:student_login')

    if request.method == 'POST':
        # Capture the existing resume name BEFORE binding the form, since form validation
        # updates the bound instance in-memory with the new uploaded file
        old_resume_name = student.resume.name if (student.resume and student.resume.name) else None
        old_storage = student.resume.storage if student.resume else None

        form = ResumeUploadForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            try:
                new_student = form.save()
            except Exception:
                messages.error(request, 'Failed to save resume. Please try again.')
                return render(request, 'students/upload_resume.html', {'form': form, 'student': student})

            # If replacement succeeded and an older resume existed, delete the old file safely from storage
            if old_resume_name and old_storage and old_resume_name != new_student.resume.name:
                try:
                    old_storage.delete(old_resume_name)
                except Exception:
                    pass
            messages.success(request, 'Resume uploaded successfully!')
            return redirect('students:dashboard')
    else:
        form = ResumeUploadForm(instance=student)

    context = {
        'form': form,
        'student': student,
    }
    return render(request, 'students/upload_resume.html', context)


@student_required
def download_resume(request):
    """Allow students to download their own resume, streamed via FileResponse."""
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('accounts:student_login')

    if not student.resume:
        messages.error(request, 'No resume uploaded yet.')
        return redirect('students:dashboard')

    try:
        if not student.resume.storage.exists(student.resume.name):
            messages.error(request, 'Resume file not found.')
            return redirect('students:dashboard')

        # Stream file in chunks using FileResponse (avoids loading into RAM)
        file_handle = student.resume.open('rb')
        response = FileResponse(
            file_handle,
            content_type='application/pdf',
            as_attachment=True,
            filename='resume.pdf'
        )
        # Prevent MIME-type sniffing attacks
        response['X-Content-Type-Options'] = 'nosniff'
        return response
    except (FileNotFoundError, ValueError):
        messages.error(request, 'Resume file not found.')
        return redirect('students:dashboard')




@student_required
def drives_list(request):
    """List all active placement drives that the student can apply to."""
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('accounts:student_login')

    # Get all active drives
    drives = Drive.objects.filter(status='active').order_by('-created_at')

    # Get drives the student has already applied to — map drive_id → status
    applied_drive_map = dict(
        Application.objects.filter(
            student=student
        ).values_list('drive_id', 'status')
    )

    # Annotate each drive with its application status (or None)
    for drive in drives:
        drive.app_status = applied_drive_map.get(drive.id)

    context = {
        'drives': drives,
        'student': student,
    }
    return render(request, 'students/drives.html', context)


@student_required
def apply_drive(request, drive_id):
    """Apply to a placement drive (one-click, requires uploaded resume)."""
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('accounts:student_login')

    drive = get_object_or_404(Drive, id=drive_id, status='active')

    # Check if student has uploaded a resume
    if not student.resume:
        messages.error(request, 'Please upload your resume before applying to drives.')
        return redirect('students:upload_resume')

    # Check if already applied
    if Application.objects.filter(drive=drive, student=student).exists():
        messages.warning(request, 'You have already applied to this drive.')
        return redirect('students:drives_list')

    # Create application
    Application.objects.create(drive=drive, student=student)
    messages.success(request, f'Successfully applied to {drive.company_name} - {drive.role}!')
    return redirect('students:drives_list')


@student_required
def my_applications(request):
    """Show all applications the student has submitted, with their current status."""
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('accounts:student_login')

    applications = Application.objects.filter(
        student=student
    ).select_related('drive').order_by('-applied_at')

    context = {
        'applications': applications,
        'student': student,
    }
    return render(request, 'students/my_applications.html', context)