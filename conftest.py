"""
Shared test factories and helpers for the TNPHelper test suite.

Uses factory_boy to create synthetic test data.
No real student data is used; all values are generated for testing only.
"""
import io
import factory
from factory.django import DjangoModelFactory, FileField
from django.contrib.auth import get_user_model
from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.backends.mysql.features import DatabaseFeatures
from students.models import Student
from tpo.models import Drive, Application

# Support running tests on dev environments with older MariaDB (< 10.5)
# CI and production use Oracle MySQL 8.4
_orig_check = BaseDatabaseWrapper.check_database_version_supported
def _relaxed_check(self):
    try:
        _orig_check(self)
    except Exception as e:
        if 'MariaDB' in str(e):
            pass
        else:
            raise
BaseDatabaseWrapper.check_database_version_supported = _relaxed_check

_orig_returning = DatabaseFeatures.can_return_columns_from_insert
def _safe_can_return(self):
    if self.connection.mysql_is_mariadb and self.connection.mysql_version < (10, 5):
        return False
    return self.connection.mysql_is_mariadb
DatabaseFeatures.can_return_columns_from_insert = property(_safe_can_return)

User = get_user_model()



# ── User factories ────────────────────────────────────────────────────────────

class StudentUserFactory(DjangoModelFactory):
    """Creates a User with role='student'."""
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"student_{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@test.example.com")
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    role = 'student'


class AdminUserFactory(DjangoModelFactory):
    """Creates a User with role='admin' (TPO staff)."""
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"tpo_{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@test.example.com")
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    role = 'admin'


# ── Student profile factory ───────────────────────────────────────────────────

class StudentFactory(DjangoModelFactory):
    """Creates a Student profile linked to a student User."""
    class Meta:
        model = Student

    user = factory.SubFactory(StudentUserFactory)
    name = factory.Sequence(lambda n: f"Test Student {n}")
    roll_no = factory.Sequence(lambda n: f"ROLL{n:04d}")
    email = factory.LazyAttribute(lambda o: o.user.email)
    branch = 'CSE'
    cgpa = factory.Faker('pydecimal', left_digits=1, right_digits=2,
                         min_value=5, max_value=10)
    skills = 'Python, Django, SQL'
    placement_status = 'not_placed'


# ── Drive factory ─────────────────────────────────────────────────────────────

class DriveFactory(DjangoModelFactory):
    """Creates a placement Drive."""
    class Meta:
        model = Drive

    company_name = factory.Sequence(lambda n: f"TechCorp {n}")
    role = 'Software Engineer'
    package = factory.Faker('pydecimal', left_digits=2, right_digits=2,
                            min_value=5, max_value=30)
    status = 'active'
    min_cgpa = 0.00


class ClosedDriveFactory(DriveFactory):
    """Creates a closed Drive."""
    status = 'closed'


class ApplicationFactory(DjangoModelFactory):
    """Creates a Drive Application."""
    class Meta:
        model = Application

    drive = factory.SubFactory(DriveFactory)
    student = factory.SubFactory(StudentFactory)
    status = 'applied'


# ── File helpers ──────────────────────────────────────────────────────────────

def make_pdf_file(name='resume.pdf', size=1024):
    """Return an InMemoryUploadedFile that looks like a real PDF."""
    from django.core.files.uploadedfile import InMemoryUploadedFile
    content = b'%PDF-1.4\n' + b'A' * (size - 9)
    return InMemoryUploadedFile(
        file=io.BytesIO(content),
        field_name='resume',
        name=name,
        content_type='application/pdf',
        size=len(content),
        charset=None,
    )


def make_fake_pdf_file(name='evil.pdf', content=b'This is not a PDF'):
    """Return a file with .pdf extension but no PDF magic bytes."""
    from django.core.files.uploadedfile import InMemoryUploadedFile
    return InMemoryUploadedFile(
        file=io.BytesIO(content),
        field_name='resume',
        name=name,
        content_type='application/pdf',
        size=len(content),
        charset=None,
    )


def make_non_pdf_file(name='script.exe'):
    """Return a non-PDF file masquerading with a .pdf extension."""
    from django.core.files.uploadedfile import InMemoryUploadedFile
    content = b'MZ\x90\x00' + b'\x00' * 100  # PE header
    return InMemoryUploadedFile(
        file=io.BytesIO(content),
        field_name='resume',
        name=name,
        content_type='application/octet-stream',
        size=len(content),
        charset=None,
    )
