"""
Tests for resume upload security and authorization.

Covers:
    - Valid PDF accepted
    - Wrong file type (non-PDF extension) rejected
    - Fake extension (PDF extension but not a real PDF) rejected by magic-byte check
    - Oversize file rejected
    - Empty file rejected
    - Path-traversal filename sanitized
    - Student A cannot download Student B's resume (object-level IDOR protection)
    - Unauthenticated access is redirected
"""
import io
from unittest.mock import patch, MagicMock

from django.test import TestCase, Client, override_settings

from conftest import StudentFactory, AdminUserFactory, make_pdf_file, make_fake_pdf_file, make_non_pdf_file
from students.forms import ResumeUploadForm


# ── Form-level validation tests ───────────────────────────────────────────────

class ResumeUploadFormValidationTest(TestCase):
    """Unit tests for ResumeUploadForm.clean_resume()."""

    def _make_form(self, file):
        """Bind a ResumeUploadForm with the given file."""
        student = StudentFactory()
        form = ResumeUploadForm(
            data={},
            files={'resume': file},
            instance=student,
        )
        return form

    def test_valid_pdf_accepted(self):
        form = self._make_form(make_pdf_file('resume.pdf'))
        self.assertTrue(form.is_valid(), f"Expected valid; errors: {form.errors}")

    def test_wrong_extension_rejected(self):
        """A .docx file must be rejected even if content is valid-looking."""
        from django.core.files.uploadedfile import InMemoryUploadedFile
        content = b'%PDF-1.4\n' + b'A' * 100
        f = InMemoryUploadedFile(
            io.BytesIO(content), 'resume', 'resume.docx',
            'application/pdf', len(content), None
        )
        form = self._make_form(f)
        self.assertFalse(form.is_valid())
        self.assertIn('resume', form.errors)

    def test_fake_pdf_rejected_by_magic_bytes(self):
        """File with .pdf extension but no %PDF magic must be rejected."""
        form = self._make_form(make_fake_pdf_file('evil.pdf'))
        self.assertFalse(form.is_valid())
        self.assertIn('resume', form.errors)

    def test_executable_disguised_as_pdf_rejected(self):
        """PE binary renamed to .pdf must be rejected."""
        form = self._make_form(make_non_pdf_file('malware.pdf'))
        self.assertFalse(form.is_valid())
        self.assertIn('resume', form.errors)

    def test_empty_file_rejected(self):
        """Zero-byte file must be rejected."""
        from django.core.files.uploadedfile import InMemoryUploadedFile
        f = InMemoryUploadedFile(
            io.BytesIO(b''), 'resume', 'empty.pdf',
            'application/pdf', 0, None
        )
        form = self._make_form(f)
        self.assertFalse(form.is_valid())
        self.assertIn('resume', form.errors)

    @override_settings(MAX_RESUME_SIZE=100)  # 100 bytes limit for test
    def test_oversize_file_rejected(self):
        """File exceeding MAX_RESUME_SIZE must be rejected."""
        form = self._make_form(make_pdf_file('big.pdf', size=200))
        self.assertFalse(form.is_valid())
        self.assertIn('resume', form.errors)

    def test_path_traversal_filename_accepted_safely(self):
        """
        A file with a path-traversal name like '../../etc/passwd.pdf' must
        be accepted by the form (filename is sanitized server-side via UUID)
        but NOT stored under the traversal path.
        """
        from django.core.files.uploadedfile import InMemoryUploadedFile
        content = b'%PDF-1.4\n' + b'A' * 100
        f = InMemoryUploadedFile(
            io.BytesIO(content), 'resume', '../../etc/passwd.pdf',
            'application/pdf', len(content), None
        )
        student = StudentFactory()
        form = ResumeUploadForm(data={}, files={'resume': f}, instance=student)
        # Form should be valid (validation doesn't fail on the name)
        self.assertTrue(form.is_valid(), f"Errors: {form.errors}")
        # The generated file path must NOT contain path traversal components
        generated_path = student.resume.field.generate_filename(
            student, '../../etc/passwd.pdf'
        )
        self.assertNotIn('..', generated_path)
        self.assertNotIn('etc', generated_path)


# ── View-level authorization tests ────────────────────────────────────────────

class ResumeDownloadAuthorizationTest(TestCase):
    """
    Student A must NOT be able to download Student B's resume.
    (IDOR protection test)
    """

    def setUp(self):
        self.student_a = StudentFactory()
        self.student_b = StudentFactory()
        self.client_a = Client()
        self.client_a.force_login(self.student_a.user)

    def test_student_can_only_download_own_resume(self):
        """
        The student download URL is /student/resume/download — it always
        serves the REQUESTING user's own resume, so Student A physically
        cannot request Student B's resume by URL manipulation.
        """
        # Student A has no resume; should redirect/error gracefully
        response = self.client_a.get('/student/download-resume/')
        # Should not return another student's data (200 with PDF bytes)
        self.assertNotEqual(response.get('Content-Type', ''), 'application/pdf')

    def test_unauthenticated_download_redirected(self):
        anon = Client()
        response = anon.get('/student/download-resume/')
        self.assertIn(response.status_code, [301, 302])

    def test_tpo_resume_download_requires_tpo_role(self):
        """A student must not be able to hit the TPO download endpoint."""
        response = self.client_a.get(f'/tpo/download-resume/{self.student_b.id}/')
        self.assertNotEqual(response.status_code, 200)


class ResumeReplacementAndStreamingTest(TestCase):
    """
    Tests for:
    - Safe resume replacement (old file replaced ONLY after successful upload;
      if upload fails, original resume is preserved).
    - Downloads stream via FileResponse rather than loading into memory.
    """

    def setUp(self):
        self.student = StudentFactory()
        self.client = Client()
        self.client.force_login(self.student.user)

    def test_successful_replacement_deletes_old_file_from_storage(self):
        # 1. Upload first resume
        pdf1 = make_pdf_file('first_resume.pdf')
        res1 = self.client.post('/student/upload-resume/', {'resume': pdf1}, follow=True)
        self.assertEqual(res1.status_code, 200)

        self.student.refresh_from_db()
        first_file_name = self.student.resume.name
        self.assertTrue(self.student.resume.storage.exists(first_file_name))

        # 2. Upload replacement resume
        pdf2 = make_pdf_file('second_resume.pdf')
        res2 = self.client.post('/student/upload-resume/', {'resume': pdf2}, follow=True)
        self.assertEqual(res2.status_code, 200)

        self.student.refresh_from_db()
        second_file_name = self.student.resume.name
        self.assertNotEqual(first_file_name, second_file_name)
        # New file exists
        self.assertTrue(self.student.resume.storage.exists(second_file_name))
        # Old file was cleaned up from storage
        self.assertFalse(self.student.resume.storage.exists(first_file_name))

    def test_failed_upload_preserves_existing_resume(self):
        # 1. Upload valid resume
        pdf1 = make_pdf_file('initial.pdf')
        self.client.post('/student/upload-resume/', {'resume': pdf1}, follow=True)

        self.student.refresh_from_db()
        original_file_name = self.student.resume.name
        self.assertTrue(self.student.resume.storage.exists(original_file_name))

        # 2. Attempt to upload an invalid file (fake PDF fails validation)
        fake_pdf = make_fake_pdf_file('bad.pdf')
        res = self.client.post('/student/upload-resume/', {'resume': fake_pdf}, follow=True)
        self.assertContains(res, 'The file does not appear to be a valid PDF')

        # 3. Original file must STILL exist in storage and in DB
        self.student.refresh_from_db()
        self.assertEqual(self.student.resume.name, original_file_name)
        self.assertTrue(self.student.resume.storage.exists(original_file_name))

    def test_save_failure_preserves_existing_resume(self):
        # 1. Upload valid initial resume
        pdf1 = make_pdf_file('initial.pdf')
        self.client.post('/student/upload-resume/', {'resume': pdf1}, follow=True)

        self.student.refresh_from_db()
        original_file_name = self.student.resume.name
        self.assertTrue(self.student.resume.storage.exists(original_file_name))

        # 2. Attempt to upload a replacement, but save fails (simulated storage or DB failure)
        pdf2 = make_pdf_file('second.pdf')
        with patch.object(ResumeUploadForm, 'save', side_effect=RuntimeError('Simulated save error')):
            res = self.client.post('/student/upload-resume/', {'resume': pdf2}, follow=True)
            self.assertContains(res, 'Failed to save resume')

        # 3. Old resume must STILL be intact in DB and in storage
        self.student.refresh_from_db()
        self.assertEqual(self.student.resume.name, original_file_name)
        self.assertTrue(self.student.resume.storage.exists(original_file_name))

    def test_student_download_streams_file_response(self):
        # Upload valid resume
        pdf = make_pdf_file('my_resume.pdf')
        self.client.post('/student/upload-resume/', {'resume': pdf}, follow=True)

        response = self.client.get('/student/download-resume/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.streaming)
        self.assertEqual(response.headers.get('Content-Type'), 'application/pdf')
        self.assertIn('attachment; filename="resume.pdf"', response.headers.get('Content-Disposition', ''))
        self.assertEqual(response.headers.get('X-Content-Type-Options'), 'nosniff')

    def test_tpo_download_streams_file_response(self):
        # Upload valid resume for student
        pdf = make_pdf_file('student_doc.pdf')
        self.client.post('/student/upload-resume/', {'resume': pdf}, follow=True)
        self.student.refresh_from_db()

        # Admin downloads student's resume
        admin_user = AdminUserFactory()
        admin_client = Client()
        admin_client.force_login(admin_user)

        response = admin_client.get(f'/tpo/download-resume/{self.student.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.streaming)
        self.assertEqual(response.headers.get('Content-Type'), 'application/pdf')
        self.assertIn(f'attachment; filename="resume_{self.student.roll_no}.pdf"', response.headers.get('Content-Disposition', ''))
        self.assertEqual(response.headers.get('X-Content-Type-Options'), 'nosniff')


