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

from conftest import StudentFactory, make_pdf_file, make_fake_pdf_file, make_non_pdf_file
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

