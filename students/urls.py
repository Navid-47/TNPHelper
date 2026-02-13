"""
URL patterns for students app.
All routes are under /student/ prefix.
"""
from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    # Dashboard and Profile
    path('dashboard/', views.student_dashboard, name='dashboard'),
    path('profile/', views.student_profile, name='profile'),

    # Resume Management
    path('upload-resume/', views.upload_resume, name='upload_resume'),
    path('download-resume/', views.download_resume, name='download_resume'),

    # Placement Drives
    path('drives/', views.drives_list, name='drives_list'),
    path('drives/<int:drive_id>/apply', views.apply_drive, name='apply_drive'),
]