"""
Main URL configuration for resume_bank project.

URL Prefixes:
    /           → core app (landing page)
    /auth/      → accounts app (login, register, logout)
    /student/   → students app (dashboard, profile, resume, drives)
    /tpo/       → tpo app (admin dashboard, analytics, drives management)
    /admin/     → Django admin panel
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django admin panel
    path('admin/', admin.site.urls),

    # Core — Landing page
    path('', include('core.urls')),

    # Accounts — Authentication (login, register, logout)
    path('auth/', include('accounts.urls')),

    # Student portal
    path('student/', include('students.urls')),

    # TPO admin portal
    path('tpo/', include('tpo.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers
handler404 = 'core.views.custom_404'
handler500 = 'core.views.custom_500'