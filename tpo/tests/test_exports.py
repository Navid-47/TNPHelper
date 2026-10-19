"""
Tests for TPO export security: CSV injection and ZIP path traversal.

Covers:
    - Only TPO/admin users can trigger CSV export
    - Only TPO/admin users can trigger ZIP bulk download
    - CSV cells starting with =, +, -, @ are prefixed with ' to neutralize formulas
    - ZIP archive entry names contain no path traversal components
"""
import csv
import io
import zipfile

from django.test import TestCase, Client
from django.core.files.base import ContentFile

from conftest import StudentFactory, AdminUserFactory, DriveFactory


class CSVExportAccessTest(TestCase):
    """Only TPO admins can export the CSV."""

    def setUp(self):
        self.admin = AdminUserFactory()
        self.student = StudentFactory()
        self.admin_client = Client()
        self.student_client = Client()
        self.admin_client.force_login(self.admin)
        self.student_client.force_login(self.student.user)

    def test_admin_can_export_csv(self):
        response = self.admin_client.get('/tpo/export-csv/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/csv', response['Content-Type'])

    def test_student_cannot_export_csv(self):
        response = self.student_client.get('/tpo/export-csv/')
        self.assertNotEqual(response.status_code, 200)

    def test_anonymous_cannot_export_csv(self):
        response = Client().get('/tpo/export-csv/')
        self.assertIn(response.status_code, [301, 302])


class CSVInjectionProtectionTest(TestCase):
    """CSV formula-injection cells must be prefixed with a single quote."""

    INJECTION_PREFIXES = ('=', '+', '-', '@')

    def setUp(self):
        self.admin = AdminUserFactory()
        self.client = Client()
        self.client.force_login(self.admin)

    def _create_student_with_name(self, name, skills='Python'):
        s = StudentFactory(name=name, skills=skills)
        return s

    def _get_csv_rows(self):
        response = self.client.get('/tpo/export-csv/')
        content = response.content.decode('utf-8')
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)
        return rows  # rows[0] = header

    def test_formula_in_name_is_neutralized(self):
        """Student name starting with '=' must be prefixed with ' in CSV."""
        self._create_student_with_name('=HYPERLINK("http://evil.com","click")')
        rows = self._get_csv_rows()
        # Find the data row (index 1+)
        for row in rows[1:]:
            name_cell = row[1]  # 'Name' column
            if 'HYPERLINK' in name_cell:
                self.assertTrue(
                    name_cell.startswith("'"),
                    f"Formula cell not sanitized: {name_cell!r}"
                )

    def test_plus_prefix_neutralized(self):
        self._create_student_with_name('+1-2-3')
        rows = self._get_csv_rows()
        for row in rows[1:]:
            if '+1-2-3' in row[1] or "'+1-2-3" in row[1]:
                name_cell = row[1]
                if name_cell.lstrip("'").startswith('+'):
                    self.assertTrue(name_cell.startswith("'"), f"Not sanitized: {name_cell!r}")

    def test_at_prefix_neutralized(self):
        self._create_student_with_name('@SUM(1+1)')
        rows = self._get_csv_rows()
        for row in rows[1:]:
            if '@SUM' in row[1] or "'@SUM" in row[1]:
                self.assertTrue(row[1].startswith("'"), f"Not sanitized: {row[1]!r}")


class ZipExportAccessTest(TestCase):
    """Only TPO admins can bulk-download resumes as ZIP."""

    def setUp(self):
        self.admin = AdminUserFactory()
        self.student = StudentFactory()
        self.admin_client = Client()
        self.student_client = Client()
        self.admin_client.force_login(self.admin)
        self.student_client.force_login(self.student.user)

    def test_admin_can_download_zip(self):
        response = self.admin_client.get('/tpo/bulk-download/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('application/zip', response['Content-Type'])

    def test_student_cannot_download_zip(self):
        response = self.student_client.get('/tpo/bulk-download/')
        self.assertNotEqual(response.status_code, 200)

    def test_anonymous_cannot_download_zip(self):
        response = Client().get('/tpo/bulk-download/')
        self.assertIn(response.status_code, [301, 302])


class ZipPathTraversalTest(TestCase):
    """ZIP archive must not contain path traversal entry names."""

    def setUp(self):
        self.admin = AdminUserFactory()
        self.client = Client()
        self.client.force_login(self.admin)

    def test_zip_entry_names_have_no_path_traversal(self):
        """
        Create students with dangerous names and verify the ZIP entry names
        do not contain '..' or absolute paths.
        """
        StudentFactory(
            name='../../../etc/shadow',
            roll_no='EVIL001',
        ).resume.save('test.pdf', ContentFile(b'%PDF-1.4\n'), save=True)

        StudentFactory(
            name='normal student',
            roll_no='NORM001',
        ).resume.save('test.pdf', ContentFile(b'%PDF-1.4\n'), save=True)

        response = self.client.get('/tpo/bulk-download/')
        self.assertEqual(response.status_code, 200)

        # Parse the ZIP and check every entry name
        zip_bytes = io.BytesIO(response.content)
        with zipfile.ZipFile(zip_bytes, 'r') as zf:
            for name in zf.namelist():
                self.assertNotIn('..', name, f"Path traversal in ZIP entry: {name}")
                self.assertFalse(name.startswith('/'), f"Absolute path in ZIP entry: {name}")
