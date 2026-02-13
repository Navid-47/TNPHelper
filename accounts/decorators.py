"""
Custom decorators for role-based access control.

Usage:
    @admin_required   — Only TPO admins can access
    @student_required — Only students can access
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def admin_required(view_func):
    """
    Decorator that restricts access to TPO admin users only.
    First checks if user is logged in, then checks if role is 'admin'.
    """
    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_admin:
            messages.error(request, 'Access denied. TPO admin privileges required.')
            return redirect('core:home')
        return view_func(request, *args, **kwargs)
    return wrapper


def student_required(view_func):
    """
    Decorator that restricts access to student users only.
    First checks if user is logged in, then checks if role is 'student'.
    """
    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_student:
            messages.error(request, 'Access denied. Student privileges required.')
            return redirect('core:home')
        return view_func(request, *args, **kwargs)
    return wrapper
