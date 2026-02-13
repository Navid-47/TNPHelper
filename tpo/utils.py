"""
Utility functions for the TPO admin portal.
Shared helpers for filtering, CSV export, and ZIP generation.
"""
from django.db.models import Q


def apply_student_filters(students, form):
    """
    Apply filter and sorting to a Student queryset using the StudentFilterForm.
    This is used by the dashboard, CSV export, and bulk download views.
    
    Args:
        students: QuerySet of Student objects
        form: A valid StudentFilterForm instance
    
    Returns:
        Filtered and sorted QuerySet
    """
    if not form.is_valid():
        return students.order_by('-created_at')

    # Search by name or roll number
    search = form.cleaned_data.get('search')
    if search:
        students = students.filter(
            Q(name__icontains=search) | Q(roll_no__icontains=search)
        )

    # Filter by branch
    branch = form.cleaned_data.get('branch')
    if branch:
        students = students.filter(branch=branch)

    # Filter by CGPA range
    cgpa_min = form.cleaned_data.get('cgpa_min')
    if cgpa_min is not None:
        students = students.filter(cgpa__gte=cgpa_min)

    cgpa_max = form.cleaned_data.get('cgpa_max')
    if cgpa_max is not None:
        students = students.filter(cgpa__lte=cgpa_max)

    # Filter by skills (match any comma-separated skill)
    skills = form.cleaned_data.get('skills')
    if skills:
        for skill in [s.strip() for s in skills.split(',') if s.strip()]:
            students = students.filter(skills__icontains=skill)

    # Filter by placement status
    placement_status = form.cleaned_data.get('placement_status')
    if placement_status:
        students = students.filter(placement_status=placement_status)

    # Apply sorting
    sort_by = form.cleaned_data.get('sort_by')
    if sort_by:
        students = students.order_by(sort_by)
    else:
        students = students.order_by('-created_at')

    return students
