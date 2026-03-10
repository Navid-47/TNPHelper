"""
Views for the core app — serves the landing page and error handlers.
"""
from django.shortcuts import render


def home(request):
    """Render the landing page."""
    return render(request, 'home.html')


def custom_404(request, exception):
    """Custom 404 error page."""
    return render(request, '404.html', status=404)


def custom_500(request):
    """Custom 500 error page."""
    return render(request, '500.html', status=500)
