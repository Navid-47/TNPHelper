"""
Tests for placement drive application flow.

Covers:
    - Student can apply to an active drive (with resume)
    - Duplicate application is rejected gracefully
    - Applying to a closed/expired drive returns 404
    - Student without a resume cannot apply
    - Application status appears in my-applications view
"""
from django.test import TestCase, Client
from conftest import StudentFactory, DriveFactory, ClosedDriveFactory, ApplicationFactory


class DriveApplicationTest(TestCase):
    """Tests for the drive application flow."""

    def setUp(self):
        self.student = StudentFactory()
        self.drive = DriveFactory()
        self.client = Client()
        self.client.force_login(self.student.user)

    def test_drives_list_accessible_to_student(self):
        response = self.client.get('/student/drives/')
        self.assertEqual(response.status_code, 200)

    def test_student_can_apply_to_active_drive_with_resume(self):
        """Student with an uploaded resume can submit an application."""
        # Give the student a mock resume path
        from django.core.files.base import ContentFile
        self.student.resume.save('test.pdf', ContentFile(b'%PDF-1.4\ntest'), save=True)

        url = f'/student/drives/{self.drive.id}/apply'
        response = self.client.get(url, follow=True)
        # Should end on drives list (200) after applying
        self.assertEqual(response.status_code, 200)

        # Confirm application was created
        from tpo.models import Application
        self.assertTrue(
            Application.objects.filter(drive=self.drive, student=self.student).exists()
        )

    def test_student_cannot_apply_without_resume(self):
        """Applying without a resume should redirect to upload page."""
        # Ensure student has no resume
        self.student.resume = None
        self.student.save()

        url = f'/student/drives/{self.drive.id}/apply'
        response = self.client.get(url, follow=True)
        # Should redirect to upload_resume (follow=True gives 200 on final page)
        # Check the redirect chain contains upload-resume
        redirect_urls = [r[0] for r in response.redirect_chain]
        self.assertTrue(
            any('upload-resume' in u for u in redirect_urls),
            msg=f"Expected redirect to upload-resume, got chain: {redirect_urls}"
        )

    def test_duplicate_application_handled_gracefully(self):
        """Applying to the same drive twice must not create a duplicate."""
        ApplicationFactory(drive=self.drive, student=self.student)

        # Resume required for the view check
        from django.core.files.base import ContentFile
        self.student.resume.save('test.pdf', ContentFile(b'%PDF-1.4\ntest'), save=True)

        url = f'/student/drives/{self.drive.id}/apply'
        self.client.get(url, follow=True)

        from tpo.models import Application
        count = Application.objects.filter(drive=self.drive, student=self.student).count()
        self.assertEqual(count, 1, "Duplicate application must not be created")

    def test_apply_to_closed_drive_returns_404(self):
        """Applying to a non-active drive must return 404."""
        closed_drive = ClosedDriveFactory()
        url = f'/student/drives/{closed_drive.id}/apply'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_my_applications_shows_student_applications(self):
        ApplicationFactory(drive=self.drive, student=self.student)
        response = self.client.get('/student/my-applications/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.drive.company_name)
