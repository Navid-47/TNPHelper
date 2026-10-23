"""
Storage backends for resume file handling.

Strategy:
  - When AWS_STORAGE_BUCKET_NAME is set (production / staging on AWS), resumes
    are stored in a *private* S3 bucket.  Pre-signed URLs are generated on-demand
    so files are never publicly accessible without authentication.
  - When the env var is absent (local dev / CI), files go to MEDIA_ROOT on disk.

Switching between the two requires ONLY setting/unsetting the four AWS_* env vars
in .env — no code changes are needed.

Usage (views):
    from students.storage import get_resume_url, get_resume_content
    url = get_resume_url(student)          # pre-signed URL (S3) or view URL (local)
    content_iter = get_resume_content(student)  # streaming iterator for FileResponse
"""
import os
import boto3
from django.conf import settings
from django.core.files.storage import FileSystemStorage


# ── Local dev fallback ─────────────────────────────────────────────────────────

class LocalResumeStorage(FileSystemStorage):
    """
    Stores resume files on local disk under MEDIA_ROOT/resumes/.
    Used when AWS credentials are not configured.
    """
    def __init__(self):
        location = os.path.join(settings.MEDIA_ROOT, 'resumes')
        super().__init__(location=location)


# ── S3 private backend ─────────────────────────────────────────────────────────

class PrivateS3ResumeStorage:
    """
    Stores resume files in a *private* S3 bucket.

    Files are uploaded with ACL private (bucket's default when ACLs are
    disabled, as is the standard for new buckets).  Retrieval generates a
    time-limited pre-signed URL so the file content is never publicly exposed.

    This class intentionally does NOT subclass django-storages S3Boto3Storage
    to keep things explicit; it's used only for resume files and delegates
    everything else to the standard storage.
    """

    def __init__(self):
        self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        self.region = getattr(settings, 'AWS_S3_REGION_NAME', None)
        self.expiry = getattr(settings, 'AWS_S3_PRESIGNED_URL_EXPIRY', 300)  # seconds

        session_kwargs = {}
        if getattr(settings, 'AWS_ACCESS_KEY_ID', None):
            session_kwargs['aws_access_key_id'] = settings.AWS_ACCESS_KEY_ID
        if getattr(settings, 'AWS_SECRET_ACCESS_KEY', None):
            session_kwargs['aws_secret_access_key'] = settings.AWS_SECRET_ACCESS_KEY
        if self.region:
            session_kwargs['region_name'] = self.region

        self._session = boto3.session.Session(**session_kwargs)
        self._s3 = self._session.client('s3')

    # ── Core helpers ──────────────────────────────────────────────────────────

    def save(self, name, content, extra_args=None):
        """Upload a file-like object to S3 under *name* (key)."""
        put_kwargs = {'ContentType': 'application/pdf'}
        if extra_args:
            put_kwargs.update(extra_args)
        content.seek(0)
        self._s3.upload_fileobj(content, self.bucket_name, name, ExtraArgs=put_kwargs)
        return name

    def delete(self, name):
        """Delete an object from S3. Silently ignored if it doesn't exist."""
        try:
            self._s3.delete_object(Bucket=self.bucket_name, Key=name)
        except Exception:
            pass

    def exists(self, name):
        """Return True if the S3 object exists."""
        try:
            self._s3.head_object(Bucket=self.bucket_name, Key=name)
            return True
        except Exception:
            return False

    def presigned_url(self, name, expiry=None):
        """Generate a pre-signed GET URL valid for *expiry* seconds (default 5 min)."""
        return self._s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket_name, 'Key': name},
            ExpiresIn=expiry or self.expiry,
        )

    def open(self, name):
        """Return a streaming body (file-like) for a given S3 key."""
        obj = self._s3.get_object(Bucket=self.bucket_name, Key=name)
        return obj['Body']


# ── Public helpers used by views ───────────────────────────────────────────────

def _using_s3():
    """Return True when S3 is configured (bucket name env var is set)."""
    return bool(getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None))


def get_resume_url(student, expiry=None):
    """
    Return the best URL to access a student's resume.

    - S3 mode  → time-limited pre-signed URL (direct browser download from S3)
    - Local    → None (caller should use the Django download view instead)
    """
    if not student.resume:
        return None
    if _using_s3():
        storage = PrivateS3ResumeStorage()
        return storage.presigned_url(student.resume.name, expiry=expiry)
    return None  # Local: views handle streaming


def get_resume_content(student):
    """
    Return a file-like streaming object for the student's resume.
    Used by Django FileResponse to stream PDF bytes to the browser.
    """
    if _using_s3():
        storage = PrivateS3ResumeStorage()
        return storage.open(student.resume.name)
    # Local filesystem — open via Django's FileField
    return student.resume.open('rb')
