"""
Storage helper for resume file access.

Provides a thin abstraction layer over the local filesystem so that
switching resumes to private S3 with signed URLs (in future) only
requires changes here — not in views.

Usage:
    from students.storage import ResumeStorage
    storage = ResumeStorage()
    content = storage.open(student.resume.name)  # returns file-like object
"""
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os


class ResumeStorage(FileSystemStorage):
    """
    Custom storage for student resumes.

    Stores files in MEDIA_ROOT/resumes/.
    This class exists as an extension point: to switch to private S3
    storage with signed URLs, subclass or replace this class and update
    students/models.py to reference the new storage backend.
    """

    def __init__(self):
        location = os.path.join(settings.MEDIA_ROOT, 'resumes')
        super().__init__(location=location)
