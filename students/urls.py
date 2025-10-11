"""
URL patterns for students app.
"""
from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    # Authentication
    path('register/', views.student_register, name='register'),
    path('login/', views.student_login, name='login'),
    path('logout/', views.student_logout, name='logout'),
    
    # Dashboard and Profile
    path('dashboard/', views.student_dashboard, name='dashboard'),
    path('profile/', views.student_profile, name='profile'),
    
    # Resume Management
    path('upload-resume/', views.upload_resume, name='upload_resume'),
    path('download-resume/', views.download_resume, name='download_resume'),
] 