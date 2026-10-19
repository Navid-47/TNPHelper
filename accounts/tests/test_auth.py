"""
Tests for authentication, routing, and role-based access control.

Covers:
    - Anonymous users are redirected from all protected routes
    - Student cannot access TPO-only views
    - TPO can access TPO views
    - Students can access student views
    - Login flow: valid credentials, invalid credentials, wrong role
"""
from django.test import TestCase, Client
from django.urls import reverse
from conftest import StudentFactory, AdminUserFactory, StudentFactory


class AnonymousRedirectTest(TestCase):
    """Anonymous users must be redirected from all protected routes."""

    STUDENT_PROTECTED_URLS = [
        '/student/dashboard',
        '/student/profile',
        '/student/resume/upload',
        '/student/resume/download',
        '/student/drives/',
        '/student/applications/',
    ]

    TPO_PROTECTED_URLS = [
        '/tpo/',
        '/tpo/analytics/',
        '/tpo/drives/',
        '/tpo/export/csv/',
        '/tpo/export/zip/',
    ]

    def setUp(self):
        self.client = Client()

    def test_student_routes_redirect_anonymous(self):
        for url in self.STUDENT_PROTECTED_URLS:
            with self.subTest(url=url):
                response = self.client.get(url, follow=False)
                self.assertIn(
                    response.status_code, [301, 302],
                    msg=f"Expected redirect for anonymous on {url}, got {response.status_code}"
                )

    def test_tpo_routes_redirect_anonymous(self):
        for url in self.TPO_PROTECTED_URLS:
            with self.subTest(url=url):
                response = self.client.get(url, follow=False)
                self.assertIn(
                    response.status_code, [301, 302],
                    msg=f"Expected redirect for anonymous on {url}, got {response.status_code}"
                )


class RoleAccessTest(TestCase):
    """Students cannot access TPO views; TPO can; and vice-versa."""

    def setUp(self):
        self.student = StudentFactory()
        self.admin_user = AdminUserFactory()
        self.student_client = Client()
        self.admin_client = Client()
        self.student_client.force_login(self.student.user)
        self.admin_client.force_login(self.admin_user)

    def test_student_cannot_access_tpo_dashboard(self):
        response = self.student_client.get('/tpo/')
        # Should redirect (not 200)
        self.assertNotEqual(response.status_code, 200)

    def test_student_cannot_access_tpo_analytics(self):
        response = self.student_client.get('/tpo/analytics/')
        self.assertNotEqual(response.status_code, 200)

    def test_student_cannot_access_csv_export(self):
        response = self.student_client.get('/tpo/export/csv/')
        self.assertNotEqual(response.status_code, 200)

    def test_admin_can_access_tpo_dashboard(self):
        response = self.admin_client.get('/tpo/')
        self.assertEqual(response.status_code, 200)

    def test_admin_cannot_access_student_dashboard(self):
        """TPO admin should not be able to use the student portal."""
        response = self.admin_client.get('/student/dashboard')
        self.assertNotEqual(response.status_code, 200)

    def test_student_can_access_own_dashboard(self):
        response = self.student_client.get('/student/dashboard')
        self.assertEqual(response.status_code, 200)


class StudentLoginTest(TestCase):
    """Login flow tests."""

    def setUp(self):
        self.student = StudentFactory()
        self.client = Client()

    def test_valid_student_login(self):
        response = self.client.post('/auth/student/login', {
            'username': self.student.user.username,
            'password': 'testpass123',
        }, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_invalid_password_rejected(self):
        response = self.client.post('/auth/student/login', {
            'username': self.student.user.username,
            'password': 'wrongpassword',
        })
        # Should not redirect to dashboard
        self.assertNotEqual(response.get('Location', ''), '/student/dashboard')

    def test_admin_cannot_use_student_login(self):
        """TPO admin credentials must not work on the student login form."""
        admin = AdminUserFactory()
        response = self.client.post('/auth/student/login', {
            'username': admin.username,
            'password': 'testpass123',
        })
        # Login should fail (user is not a student)
        self.assertFalse(response.wsgi_request.user.is_authenticated
                         or response.wsgi_request.user.role != 'student')
