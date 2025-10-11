"""
Views for TPO dashboard and student management.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from students.models import Student
from .forms import TPOLoginForm, StudentFilterForm, PlacementStatusUpdateForm
import csv
import os
import zipfile
from io import StringIO
from collections import Counter

def is_tpo(user):
    """Check if user is TPO (staff member)."""
    return user.is_authenticated and user.is_staff

def tpo_login(request):
    """
    Handle TPO login.
    """
    if request.method == 'POST':
        form = TPOLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None and user.is_staff:
                login(request, user)
                messages.success(request, f'Welcome, {user.get_full_name() or user.username}!')
                return redirect('tpo:dashboard')
            else:
                messages.error(request, 'Invalid credentials or insufficient permissions.')
    else:
        form = TPOLoginForm()
    
    return render(request, 'tpo/login.html', {'form': form})

@login_required
@user_passes_test(is_tpo)
def tpo_dashboard(request):
    """
    TPO dashboard with student list and filtering.
    """
    # Get filter form data
    form = StudentFilterForm(request.GET)
    students = Student.objects.all()
    
    if form.is_valid():
        # Apply filters
        search = form.cleaned_data.get('search')
        if search:
            students = students.filter(
                Q(name__icontains=search) | Q(roll_no__icontains=search)
            )
        
        branch = form.cleaned_data.get('branch')
        if branch:
            students = students.filter(branch=branch)
        
        cgpa_min = form.cleaned_data.get('cgpa_min')
        if cgpa_min is not None:
            students = students.filter(cgpa__gte=cgpa_min)
        
        cgpa_max = form.cleaned_data.get('cgpa_max')
        if cgpa_max is not None:
            students = students.filter(cgpa__lte=cgpa_max)
        
        skills = form.cleaned_data.get('skills')
        if skills:
            skill_list = [skill.strip() for skill in skills.split(',') if skill.strip()]
            for skill in skill_list:
                students = students.filter(skills__icontains=skill)
        
        placement_status = form.cleaned_data.get('placement_status')
        if placement_status:
            students = students.filter(placement_status=placement_status)
        
        # Apply sorting - only if sort_by is not empty
        sort_by = form.cleaned_data.get('sort_by')
        if sort_by:
            students = students.order_by(sort_by)
        else:
            # Default sorting by creation date (newest first)
            students = students.order_by('-created_at')
    else:
        # Default sorting if form is not valid
        students = students.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(students, 20)  # 20 students per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'page_obj': page_obj,
        'total_students': students.count(),
    }
    return render(request, 'tpo/dashboard.html', context)

@login_required
@user_passes_test(is_tpo)
def tpo_analytics(request):
    """
    Analytics dashboard with charts and statistics.
    """
    # Get all students
    students = Student.objects.all()
    total_students = students.count()
    
    if total_students == 0:
        context = {
            'total_students': 0,
            'no_data': True
        }
        return render(request, 'tpo/analytics.html', context)
    
    # CGPA Distribution
    cgpa_ranges = {
        '9.0-10.0': students.filter(cgpa__gte=9.0).count(),
        '8.0-8.99': students.filter(cgpa__gte=8.0, cgpa__lt=9.0).count(),
        '7.0-7.99': students.filter(cgpa__gte=7.0, cgpa__lt=8.0).count(),
        '6.0-6.99': students.filter(cgpa__gte=6.0, cgpa__lt=7.0).count(),
        'Below 6.0': students.filter(cgpa__lt=6.0).count(),
    }
    
    # Branch Distribution
    branch_stats = students.values('branch').annotate(count=Count('id')).order_by('-count')
    
    # Placement Status Distribution
    placement_stats = students.values('placement_status').annotate(count=Count('id'))
    
    # Skills Analysis
    all_skills = []
    for student in students:
        all_skills.extend(student.get_skills_list())
    
    skill_counts = Counter(all_skills)
    top_skills = dict(skill_counts.most_common(10))
    
    # Average CGPA by branch
    avg_cgpa_by_branch = students.values('branch').annotate(avg_cgpa=Avg('cgpa')).order_by('-avg_cgpa')
    
    # Placement rate
    placed_count = students.filter(placement_status='placed').count()
    placement_rate = (placed_count / total_students * 100) if total_students > 0 else 0
    
    context = {
        'total_students': total_students,
        'cgpa_ranges': cgpa_ranges,
        'branch_stats': list(branch_stats),
        'placement_stats': list(placement_stats),
        'top_skills': top_skills,
        'avg_cgpa_by_branch': list(avg_cgpa_by_branch),
        'placement_rate': round(placement_rate, 2),
        'placed_count': placed_count,
        'no_data': False
    }
    return render(request, 'tpo/analytics.html', context)

@login_required
@user_passes_test(is_tpo)
def student_detail(request, student_id):
    """
    View detailed student information.
    """
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
            'package': student.package
        })
    
    context = {
        'student': student,
        'form': form,
        'skills_list': student.get_skills_list(),
    }
    return render(request, 'tpo/student_detail.html', context)

@login_required
@user_passes_test(is_tpo)
def download_resume(request, student_id):
    """
    Download individual student resume.
    """
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

@login_required
@user_passes_test(is_tpo)
def export_csv(request):
    """
    Export filtered student data to CSV.
    """
    # Apply same filters as dashboard
    form = StudentFilterForm(request.GET)
    students = Student.objects.all()
    
    if form.is_valid():
        # Apply filters (same logic as dashboard)
        search = form.cleaned_data.get('search')
        if search:
            students = students.filter(
                Q(name__icontains=search) | Q(roll_no__icontains=search)
            )
        
        branch = form.cleaned_data.get('branch')
        if branch:
            students = students.filter(branch=branch)
        
        cgpa_min = form.cleaned_data.get('cgpa_min')
        if cgpa_min is not None:
            students = students.filter(cgpa__gte=cgpa_min)
        
        cgpa_max = form.cleaned_data.get('cgpa_max')
        if cgpa_max is not None:
            students = students.filter(cgpa__lte=cgpa_max)
        
        skills = form.cleaned_data.get('skills')
        if skills:
            skill_list = [skill.strip() for skill in skills.split(',') if skill.strip()]
            for skill in skill_list:
                students = students.filter(skills__icontains=skill)
        
        placement_status = form.cleaned_data.get('placement_status')
        if placement_status:
            students = students.filter(placement_status=placement_status)
        
        # Apply sorting - only if sort_by is not empty
        sort_by = form.cleaned_data.get('sort_by')
        if sort_by:
            students = students.order_by(sort_by)
        else:
            # Default sorting by creation date (newest first)
            students = students.order_by('-created_at')
    else:
        # Default sorting if form is not valid
        students = students.order_by('-created_at')
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students_data.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Name', 'Roll No', 'Email', 'Branch', 'CGPA', 'Skills', 
        'Placement Status', 'Company Name', 'Package (LPA)', 'Created Date'
    ])
    
    for student in students:
        writer.writerow([
            student.name,
            student.roll_no,
            student.email,
            student.get_branch_display_name(),
            student.cgpa,
            student.skills,
            student.get_placement_status_display(),
            student.company_name or '',
            student.package or '',
            student.created_at.strftime('%Y-%m-%d')
        ])
    
    return response

@login_required
@user_passes_test(is_tpo)
def bulk_download_resumes(request):
    """
    Download all resumes as a ZIP file.
    """
    # Apply same filters as dashboard
    form = StudentFilterForm(request.GET)
    students = Student.objects.all()
    
    if form.is_valid():
        # Apply filters (same logic as dashboard)
        search = form.cleaned_data.get('search')
        if search:
            students = students.filter(
                Q(name__icontains=search) | Q(roll_no__icontains=search)
            )
        
        branch = form.cleaned_data.get('branch')
        if branch:
            students = students.filter(branch=branch)
        
        cgpa_min = form.cleaned_data.get('cgpa_min')
        if cgpa_min is not None:
            students = students.filter(cgpa__gte=cgpa_min)
        
        cgpa_max = form.cleaned_data.get('cgpa_max')
        if cgpa_max is not None:
            students = students.filter(cgpa__lte=cgpa_max)
        
        skills = form.cleaned_data.get('skills')
        if skills:
            skill_list = [skill.strip() for skill in skills.split(',') if skill.strip()]
            for skill in skill_list:
                students = students.filter(skills__icontains=skill)
        
        placement_status = form.cleaned_data.get('placement_status')
        if placement_status:
            students = students.filter(placement_status=placement_status)
        
        # Apply sorting - only if sort_by is not empty
        sort_by = form.cleaned_data.get('sort_by')
        if sort_by:
            students = students.order_by(sort_by)
        else:
            # Default sorting by creation date (newest first)
            students = students.order_by('-created_at')
    else:
        # Default sorting if form is not valid
        students = students.order_by('-created_at')
    
    # Create ZIP file
    response = HttpResponse(content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="student_resumes.zip"'
    
    with zipfile.ZipFile(response, 'w') as zip_file:
        for student in students:
            if student.resume and os.path.exists(student.resume.path):
                filename = f"{student.roll_no}_{student.name}_resume.pdf"
                zip_file.write(student.resume.path, filename)
    
    return response

@login_required
@user_passes_test(is_tpo)
def tpo_logout(request):
    """
    Handle TPO logout.
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home') 