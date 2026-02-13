"""
URL patterns for TPO admin portal.
All routes are under /tpo/ prefix.
"""
from django.urls import path
from . import views

app_name = 'tpo'

urlpatterns = [
    # Dashboard and Analytics
    path('dashboard/', views.tpo_dashboard, name='dashboard'),
    path('analytics/', views.tpo_analytics, name='analytics'),

    # Student Management
    path('student/<int:student_id>/', views.student_detail, name='student_detail'),
    path('download-resume/<int:student_id>/', views.download_resume, name='download_resume'),

    # Data Exports
    path('export-csv/', views.export_csv, name='export_csv'),
    path('bulk-download/', views.bulk_download_resumes, name='bulk_download'),

    # Placement Drive Management
    path('drives/', views.drives_list, name='drives_list'),
    path('drives/create/', views.create_drive, name='create_drive'),
    path('drives/<int:drive_id>/applicants/', views.drive_applicants, name='drive_applicants'),
    path('drives/application/<int:app_id>/status/', views.update_app_status, name='update_app_status'),
]