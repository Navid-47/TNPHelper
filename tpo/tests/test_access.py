"""
Tests for TPO view access control.

Covers:
    - Student cannot access any TPO-only view
    - TPO admin can access all TPO views
    - Anonymous users are redirected from all TPO views
"""
from django.test import TestCase, Client
from conftest import StudentFactory, AdminUserFactory, DriveFactory, ApplicationFactory


class TPOAccessControlTest(TestCase):
    """Comprehensive role-based access tests for all TPO views."""

    TPO_URLS = [
        '/tpo/dashboard/',
        '/tpo/analytics/',
        '/tpo/export-csv/',
        '/tpo/bulk-download/',
        '/tpo/drives/',
        '/tpo/drives/create/',
    ]

    def setUp(self):
        self.admin = AdminUserFactory()
        self.student = StudentFactory()

        self.admin_client = Client()
        self.student_client = Client()
        self.anon_client = Client()

        self.admin_client.force_login(self.admin)
        self.student_client.force_login(self.student.user)

    def test_admin_can_access_all_tpo_views(self):
        for url in self.TPO_URLS:
            with self.subTest(url=url):
                response = self.admin_client.get(url)
                self.assertEqual(
                    response.status_code, 200,
                    msg=f"TPO admin expected 200 on {url}, got {response.status_code}"
                )

    def test_student_cannot_access_any_tpo_view(self):
        for url in self.TPO_URLS:
            with self.subTest(url=url):
                response = self.student_client.get(url)
                self.assertNotEqual(
                    response.status_code, 200,
                    msg=f"Student must NOT get 200 on {url}"
                )

    def test_anonymous_redirected_from_all_tpo_views(self):
        for url in self.TPO_URLS:
            with self.subTest(url=url):
                response = self.anon_client.get(url)
                self.assertIn(
                    response.status_code, [301, 302],
                    msg=f"Anonymous expected redirect on {url}, got {response.status_code}"
                )

    def test_student_detail_requires_admin(self):
        student = StudentFactory()
        url = f'/tpo/student/{student.id}/'
        response = self.student_client.get(url)
        self.assertNotEqual(response.status_code, 200)

    def test_resume_download_requires_admin(self):
        student = StudentFactory()
        url = f'/tpo/download-resume/{student.id}/'
        response = self.student_client.get(url)
        self.assertNotEqual(response.status_code, 200)

    def test_drive_applicants_requires_admin(self):
        drive = DriveFactory()
        url = f'/tpo/drives/{drive.id}/applicants/'
        response = self.student_client.get(url)
        self.assertNotEqual(response.status_code, 200)
