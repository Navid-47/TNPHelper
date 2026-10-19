"""
Main URL configuration for resume_bank project.

URL Prefixes:
    /           → core app (landing page)
    /auth/      → accounts app (login, register, logout)
    /student/   → students app (dashboard, profile, resume, drives)
    /tpo/       → tpo app (admin dashboard, analytics, drives management)
    /admin/     → Django admin panel
    /healthz/   → unauthenticated health check (GET/HEAD)
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import healthz

urlpatterns = [
    # Health check — unauthenticated, no CSRF, must be first
    path('healthz/', healthz, name='healthz'),

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

# Serve media files during development ONLY.
# In production, Nginx serves static files; media is NOT served publicly.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers
handler404 = 'core.views.custom_404'
handler500 = 'core.views.custom_500'