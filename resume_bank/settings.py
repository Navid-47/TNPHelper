"""
Django settings for resume_bank project.
Resume Bank Management System — Training & Placement Cell

All sensitive values MUST be provided via environment variables.
See .env.example for a full list of required variables.
"""

import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
from decouple import config, Csv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ──────────────────────────────────────────────
# Environment helpers
# ──────────────────────────────────────────────

DEBUG = config('DEBUG', default=False, cast=bool)

# SECRET_KEY: required in production; a labelled insecure fallback is
# allowed ONLY when DEBUG=True (dev laptops, CI with DEBUG=True).
_DEV_ONLY_SECRET_KEY = 'django-insecure-dev-only-key-NOT-for-production-use'

if DEBUG:
    SECRET_KEY = config('SECRET_KEY', default=_DEV_ONLY_SECRET_KEY)
else:
    SECRET_KEY = config('SECRET_KEY', default=None)
    if not SECRET_KEY:
        raise ImproperlyConfigured(
            "SECRET_KEY environment variable is required when DEBUG=False. "
            "Set it to a long, random, unique string. "
            "See .env.example for the full list of required variables."
        )

# ALLOWED_HOSTS: never defaults to ['*']
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost,127.0.0.1',
    cast=Csv(),
)

# CSRF_TRUSTED_ORIGINS (needed for proxied HTTPS setups)
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='',
    cast=Csv(),
)

# ──────────────────────────────────────────────
# Application definition
# ──────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party
    'crispy_forms',
    'crispy_bootstrap5',
    # Project apps
    'accounts',      # Authentication & custom User model
    'students',      # Student portal
    'tpo',           # TPO admin portal
    'core',          # Shared templates & home page
]

# ──────────────────────────────────────────────
# Custom User Model
# ──────────────────────────────────────────────
AUTH_USER_MODEL = 'accounts.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # serve static files efficiently
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'resume_bank.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'resume_bank.wsgi.application'

# ──────────────────────────────────────────────
# Database — MySQL (all values from env)
# In production (DEBUG=False), DB_NAME, DB_USER, DB_PASSWORD, and DB_HOST
# are mandatory and must be explicitly configured using a least-privilege account.
# ──────────────────────────────────────────────
if DEBUG:
    DB_NAME = config('DB_NAME', default='tnp_db')
    DB_USER = config('DB_USER', default='tnphelper')
    DB_PASSWORD = config('DB_PASSWORD', default='')
    DB_HOST = config('DB_HOST', default='localhost')
    DB_PORT = config('DB_PORT', default='3306')
else:
    DB_NAME = config('DB_NAME', default=None)
    DB_USER = config('DB_USER', default=None)
    DB_PASSWORD = config('DB_PASSWORD', default=None)
    DB_HOST = config('DB_HOST', default=None)
    DB_PORT = config('DB_PORT', default='3306')

    missing_db_vars = []
    if not DB_NAME:
        missing_db_vars.append('DB_NAME')
    if not DB_USER:
        missing_db_vars.append('DB_USER')
    if DB_PASSWORD is None or DB_PASSWORD == '':
        missing_db_vars.append('DB_PASSWORD')
    if not DB_HOST:
        missing_db_vars.append('DB_HOST')

    if missing_db_vars:
        raise ImproperlyConfigured(
            f"Production database configuration error: The following required database "
            f"environment variable(s) must be explicitly configured when DEBUG=False: "
            f"{', '.join(missing_db_vars)}. Ensure a dedicated, least-privilege database "
            f"account is used. See .env.example for details."
        )

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# ──────────────────────────────────────────────
# Password validation
# ──────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ──────────────────────────────────────────────
# Internationalization
# ──────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ──────────────────────────────────────────────
# Static files (CSS, JavaScript, Images)
# ──────────────────────────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ──────────────────────────────────────────────
# Media files (Uploaded resumes — local fallback)
# NOTE: MEDIA_URL is intentionally NOT served in production.
# Nginx must NOT expose MEDIA_ROOT publicly.
# Resume downloads go through authenticated Django views (signed URLs on S3).
# ──────────────────────────────────────────────
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ──────────────────────────────────────────────
# AWS S3 — Private Resume Storage
# When AWS_STORAGE_BUCKET_NAME is set, resumes are stored in a private S3
# bucket and accessed via time-limited pre-signed URLs.  Leave it unset to
# fall back to local disk storage (development / CI).
# ──────────────────────────────────────────────
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='')
AWS_S3_REGION_NAME      = config('AWS_S3_REGION_NAME',      default='ap-south-1')
AWS_ACCESS_KEY_ID       = config('AWS_ACCESS_KEY_ID',       default='')
AWS_SECRET_ACCESS_KEY   = config('AWS_SECRET_ACCESS_KEY',   default='')

# Seconds a pre-signed download URL remains valid (default: 5 minutes).
# Increase if users need longer download windows (e.g. slow connections).
AWS_S3_PRESIGNED_URL_EXPIRY = config('AWS_S3_PRESIGNED_URL_EXPIRY', default=300, cast=int)

# django-storages: do NOT set a public ACL on uploaded objects
AWS_DEFAULT_ACL = None
# django-storages: use path-style S3 URLs when needed (e.g. LocalStack)
AWS_S3_ADDRESSING_STYLE = 'path'
# Prevent django-storages from appending query-string signatures to FileField.url
# (we generate our own pre-signed URLs in views / storage.py)
AWS_QUERYSTRING_AUTH = False

# ──────────────────────────────────────────────
# File Upload Settings
# MAX_RESUME_SIZE: maximum resume upload size in bytes (default 5 MB).
# Overridable via env var for flexibility.
# ──────────────────────────────────────────────
MAX_RESUME_SIZE = config('MAX_RESUME_SIZE', default=5 * 1024 * 1024, cast=int)  # 5 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = config(
    'DATA_UPLOAD_MAX_MEMORY_SIZE',
    default=10 * 1024 * 1024,  # 10 MB (must be >= MAX_RESUME_SIZE + form overhead)
    cast=int,
)
ALLOWED_UPLOAD_EXTENSIONS = ['.pdf']

# ──────────────────────────────────────────────
# Production security settings
# Active when DEBUG=False. Each is overridable by env var.
# ──────────────────────────────────────────────
if not DEBUG:
    # Redirect all HTTP → HTTPS (Nginx handles TLS; this is a safety net)
    SECURE_SSL_REDIRECT = os.getenv(
        "SECURE_SSL_REDIRECT",
        "False" if DEBUG else "True",
    ).strip().lower() in {"1", "true", "yes", "on"}
    # Allow AWS ALB health checks over HTTP
    SECURE_REDIRECT_EXEMPT = [r"^healthz/$"]

    # Tell Django it is behind an SSL-terminating proxy
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    # HSTS: 1 year; subdomains and preload left off by default to be safe
    SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=31536000, cast=int)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = config(
        'SECURE_HSTS_INCLUDE_SUBDOMAINS', default=False, cast=bool
    )
    SECURE_HSTS_PRELOAD = config('SECURE_HSTS_PRELOAD', default=False, cast=bool)

    # Cookie security
    SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=True, cast=bool)
    CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=True, cast=bool)
    SESSION_COOKIE_HTTPONLY = True

    # Content sniffing protection
    SECURE_CONTENT_TYPE_NOSNIFF = True

    # Clickjacking protection
    X_FRAME_OPTIONS = 'DENY'
else:
    # Development: relax security headers so local HTTP works normally
    SECURE_SSL_REDIRECT = os.getenv(
        "SECURE_SSL_REDIRECT",
        "False" if DEBUG else "True",
    ).strip().lower() in {"1", "true", "yes", "on"}
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

# ──────────────────────────────────────────────
# Auth URLs
# ──────────────────────────────────────────────
LOGIN_URL = '/auth/student/login'
LOGIN_REDIRECT_URL = '/student/dashboard'
LOGOUT_REDIRECT_URL = '/'

# ──────────────────────────────────────────────
# Crispy Forms (Bootstrap 5)
# ──────────────────────────────────────────────
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# ──────────────────────────────────────────────
# Default primary key field type
# ──────────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ──────────────────────────────────────────────
# Messages framework — Bootstrap alert classes
# ──────────────────────────────────────────────
from django.contrib.messages import constants as messages  # noqa: E402
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}
