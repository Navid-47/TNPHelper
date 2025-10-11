"""
URL patterns for TPO app.
"""
from django.urls import path
from . import views

app_name = 'tpo'

urlpatterns = [
    # Authentication
    path('login/', views.tpo_login, name='login'),
    path('logout/', views.tpo_logout, name='logout'),
    
    # Dashboard and Analytics
    path('dashboard/', views.tpo_dashboard, name='dashboard'),
    path('analytics/', views.tpo_analytics, name='analytics'),
    
    # Student Management
    path('student/<int:student_id>/', views.student_detail, name='student_detail'),
    path('student/<int:student_id>/download-resume/', views.download_resume, name='download_resume'),
    
    # Export and Download
    path('export-csv/', views.export_csv, name='export_csv'),
    path('bulk-download-resumes/', views.bulk_download_resumes, name='bulk_download_resumes'),
] 