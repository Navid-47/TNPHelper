"""
Views for the core app — serves the landing page.
"""
from django.shortcuts import render


def home(request):
    """Render the landing page."""
    return render(request, 'home.html')
