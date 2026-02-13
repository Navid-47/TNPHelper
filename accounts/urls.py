"""
URL patterns for the accounts app.
Handles all authentication routes under /auth/ prefix.
"""
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Student authentication
    path('student/register', views.student_register, name='student_register'),
    path('student/login', views.student_login, name='student_login'),
    path('student/logout', views.student_logout, name='student_logout'),

    # TPO admin authentication
    path('tpo/login', views.tpo_login, name='tpo_login'),
    path('tpo/logout', views.tpo_logout, name='tpo_logout'),
]
