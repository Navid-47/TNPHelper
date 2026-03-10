"""
Views for the TPO admin portal.
Handles student directory, analytics, drive management, and data exports.

All views use @admin_required to ensure only TPO admins can access them.
(Authentication views are in accounts/views.py)
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Count, Avg
from django.core.paginator import Paginator
from accounts.decorators import admin_required
from students.models import Student
from .models import Drive, Application
from .forms import StudentFilterForm, PlacementStatusUpdateForm, DriveForm, ApplicationStatusForm
from .utils import apply_student_filters
from collections import Counter
import csv
import os
import zipfile


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def get_ellipsis_page_range(page_obj, on_each_side=1, on_ends=2):
    """Build a page-number list with '...' ellipsis for large datasets."""
    num_pages = page_obj.paginator.num_pages
    current = page_obj.number

    if num_pages <= (on_each_side + on_ends) * 2 + 1:
        return list(range(1, num_pages + 1))

    pages = []
    # Left end
    for i in range(1, on_ends + 1):
        if i <= num_pages:
            pages.append(i)
    # Left ellipsis
    if current - on_each_side > on_ends + 1:
        pages.append('...')
    # Around current
    for i in range(max(on_ends + 1, current - on_each_side), min(num_pages - on_ends + 1, current + on_each_side + 1)):
        if i not in pages:
            pages.append(i)
    # Right ellipsis
    if current + on_each_side < num_pages - on_ends:
        pages.append('...')
    # Right end
    for i in range(num_pages - on_ends + 1, num_pages + 1):
        if i not in pages and i > 0:
            pages.append(i)

    return pages


# ──────────────────────────────────────────────
# Student Directory & Dashboard
# ──────────────────────────────────────────────

@admin_required
def tpo_dashboard(request):
    """TPO dashboard — student directory with search, filter, and sort."""
    form = StudentFilterForm(request.GET)
    students = apply_student_filters(Student.objects.all(), form)

    # Pagination — 20 students per page
    paginator = Paginator(students, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'form': form,
        'students': page_obj,
        'page_range': get_ellipsis_page_range(page_obj),
        'total_students': students.count(),
        'branch_choices': Student.BRANCH_CHOICES,
    }
    return render(request, 'tpo/dashboard.html', context)


@admin_required
def student_detail(request, student_id):
    """View student details and update placement status."""
    student = get_object_or_404(Student, id=student_id)

    if request.method == 'POST':
        form = PlacementStatusUpdateForm(request.POST)
        if form.is_valid():
            student.placement_status = form.cleaned_data['placement_status']
            student.company_name = form.cleaned_data.get('company_name', '')
            student.package = form.cleaned_data.get('package')
            student.save()
            messages.success(request, 'Placement status updated successfully!')
            return redirect('tpo:student_detail', student_id=student_id)
    else:
        form = PlacementStatusUpdateForm(initial={
            'placement_status': student.placement_status,
            'company_name': student.company_name,
            'package': student.package,
        })

    context = {
        'student': student,
        'form': form,
        'skills_list': student.get_skills_list(),
    }
    return render(request, 'tpo/student_detail.html', context)


# ──────────────────────────────────────────────
# Analytics
# ──────────────────────────────────────────────

@admin_required
def tpo_analytics(request):
    """Analytics dashboard with charts — CGPA, branch, placement, skills."""
    students = Student.objects.all()
    total_students = students.count()

    if total_students == 0:
        return render(request, 'tpo/analytics.html', {
            'total_students': 0, 'no_data': True
        })

    # CGPA Distribution
    cgpa_distribution = {
        '9.0-10.0': students.filter(cgpa__gte=9.0).count(),
        '8.0-8.99': students.filter(cgpa__gte=8.0, cgpa__lt=9.0).count(),
        '7.0-7.99': students.filter(cgpa__gte=7.0, cgpa__lt=8.0).count(),
        '6.0-6.99': students.filter(cgpa__gte=6.0, cgpa__lt=7.0).count(),
        'Below 6.0': students.filter(cgpa__lt=6.0).count(),
    }

    # Branch Distribution
    branch_stats = list(students.values('branch').annotate(count=Count('id')).order_by('-count'))
    # Attach human-readable branch names for templates
    branch_name_map = dict(Student.BRANCH_CHOICES)
    for item in branch_stats:
        item['branch_name'] = branch_name_map.get(item['branch'], item['branch'])

    # Placement Statistics
    placed_count = students.filter(placement_status='placed').count()
    in_process_count = students.filter(placement_status='in_process').count()
    not_placed_count = students.filter(placement_status='not_placed').count()
    placement_rate = round(placed_count / total_students * 100, 2)

    # Top Skills
    all_skills = []
    for student in students:
        all_skills.extend(student.get_skills_list())
    top_skills = dict(Counter(all_skills).most_common(10))

    # Average CGPA by branch
    avg_cgpa_by_branch = list(
        students.values('branch').annotate(avg_cgpa=Avg('cgpa')).order_by('-avg_cgpa')
    )

    # Branch-wise placement data (placed count + rate per branch)
    branch_placement = []
    for bs in branch_stats:
        branch_total = bs['count']
        branch_placed = students.filter(branch=bs['branch'], placement_status='placed').count()
        rate = round(branch_placed / branch_total * 100, 1) if branch_total > 0 else 0
        branch_placement.append({
            'branch': bs['branch'],
            'placed': branch_placed,
            'rate': rate,
        })

    context = {
        'total_students': total_students,
        'cgpa_distribution': cgpa_distribution,
        'branch_stats': branch_stats,
        'top_skills': top_skills,
        'avg_cgpa_by_branch': avg_cgpa_by_branch,
        'placement_rate': placement_rate,
        'placed_count': placed_count,
        'in_process_count': in_process_count,
        'not_placed_count': not_placed_count,
        'branch_placement': branch_placement,
        'no_data': False,
    }
    return render(request, 'tpo/analytics.html', context)


# ──────────────────────────────────────────────
# Resume Downloads
# ──────────────────────────────────────────────

@admin_required
def download_resume(request, student_id):
    """Download a specific student's resume."""
    student = get_object_or_404(Student, id=student_id)

    if not student.resume:
        messages.error(request, 'No resume uploaded for this student.')
        return redirect('tpo:student_detail', student_id=student_id)

    if os.path.exists(student.resume.path):
        with open(student.resume.path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{student.get_resume_filename()}"'
            return response
    else:
        messages.error(request, 'Resume file not found.')
        return redirect('tpo:student_detail', student_id=student_id)


# ──────────────────────────────────────────────
# Data Exports (CSV & ZIP)
# ──────────────────────────────────────────────

@admin_required
def export_csv(request):
    """Export filtered student data as a CSV file."""
    form = StudentFilterForm(request.GET)
    students = apply_student_filters(Student.objects.all(), form)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students_data.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Roll No', 'Name', 'Email', 'Branch', 'CGPA', 'Skills',
        'Status', 'Company', 'Package', 'Has Resume'
    ])

    for student in students:
        writer.writerow([
            student.roll_no,
            student.name,
            student.email,
            student.get_branch_display_name(),
            student.cgpa,
            student.skills,
            student.get_placement_status_display(),
            student.company_name or '',
            student.package or '',
            'Yes' if student.resume else 'No',
        ])

    return response


@admin_required
def bulk_download_resumes(request):
    """Download all filtered student resumes as a ZIP file."""
    form = StudentFilterForm(request.GET)
    students = apply_student_filters(Student.objects.all(), form)

    response = HttpResponse(content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="student_resumes.zip"'

    with zipfile.ZipFile(response, 'w') as zip_file:
        for student in students:
            if student.resume and os.path.exists(student.resume.path):
                filename = f"{student.roll_no}_{student.name}.pdf"
                zip_file.write(student.resume.path, filename)

    return response


# ──────────────────────────────────────────────
# Placement Drive Management
# ──────────────────────────────────────────────

@admin_required
def drives_list(request):
    """List all placement drives."""
    drives = Drive.objects.all().order_by('-created_at')

    # Add applicant count for each drive
    for drive in drives:
        drive.applicant_count = drive.applications.count()

    context = {'drives': drives}
    return render(request, 'tpo/drives/list.html', context)


@admin_required
def create_drive(request):
    """Create a new placement drive."""
    if request.method == 'POST':
        form = DriveForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Placement drive created successfully!')
            return redirect('tpo:drives_list')
    else:
        form = DriveForm()

    return render(request, 'tpo/drives/create.html', {'form': form})


@admin_required
def drive_applicants(request, drive_id):
    """View all students who applied to a specific drive."""
    drive = get_object_or_404(Drive, id=drive_id)
    applications = drive.applications.select_related('student').all()

    context = {
        'drive': drive,
        'applications': applications,
    }
    return render(request, 'tpo/drives/applicants.html', context)


@admin_required
def update_app_status(request, app_id):
    """Update an individual application's status (shortlist/reject/offer)."""
    application = get_object_or_404(Application, id=app_id)

    if request.method == 'POST':
        form = ApplicationStatusForm(request.POST)
        if form.is_valid():
            application.status = form.cleaned_data['status']
            application.save()
            messages.success(
                request,
                f'Application status for {application.student.name} updated to {application.get_status_display()}.'
            )

    return redirect('tpo:drive_applicants', drive_id=application.drive.id)