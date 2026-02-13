# System Design Document
## Resume Bank Management System — Django + MySQL Architecture

| Field | Value |
|-------|-------|
| **Document Version** | 1.0 |
| **Date** | 2026-02-13 |
| **Target Stack** | Python 3.10+, Django 5.x, MySQL 8.x, Bootstrap 5 |
| **Current Stack** | Python 3.10+, Flask 3.x, MongoDB (PyMongo) |

---

## 1. Architecture Overview

The system follows the standard **Django MVT (Model-View-Template)** architecture with clear separation of concerns.

```
┌──────────────────────────────────────────────────┐
│                    Client (Browser)               │
│            HTML5 / Bootstrap 5 / Chart.js         │
└────────────────────────┬─────────────────────────┘
                         │  HTTP / HTTPS
┌────────────────────────▼─────────────────────────┐
│                   Django Application              │
│  ┌─────────┐  ┌──────────┐  ┌─────────────────┐  │
│  │  URLs   │→ │  Views   │→ │   Templates     │  │
│  │ (routes)│  │ (logic)  │  │   (Jinja2/DTL)  │  │
│  └─────────┘  └────┬─────┘  └─────────────────┘  │
│                     │                             │
│  ┌──────────────────▼──────────────────────────┐  │
│  │              Models (ORM)                   │  │
│  │   User | Student | Drive | Application     │  │
│  └──────────────────┬──────────────────────────┘  │
│                     │                             │
│  ┌──────────────────▼──────────────────────────┐  │
│  │           Forms (Django Forms)              │  │
│  └─────────────────────────────────────────────┘  │
│                                                   │
│  ┌─────────────────────────────────────────────┐  │
│  │      Middleware (CSRF, Auth, Session)       │  │
│  └─────────────────────────────────────────────┘  │
└────────────────────────┬─────────────────────────┘
                         │
          ┌──────────────▼──────────────┐
          │      MySQL 8.x Database     │
          │   ┌─────┐ ┌────────┐        │
          │   │users│ │students│        │
          │   └─────┘ └────────┘        │
          │   ┌──────┐ ┌────────────┐   │
          │   │drives│ │applications│   │
          │   └──────┘ └────────────┘   │
          └──────────────┬──────────────┘
                         │
          ┌──────────────▼──────────────┐
          │       File System           │
          │   media/resumes/*.pdf       │
          └─────────────────────────────┘
```

---

## 2. Django Project Structure

```
tnp_project/
├── manage.py
├── requirements.txt
├── .env
├── tnp_project/                    # Django project config
│   ├── __init__.py
│   ├── settings.py                 # DB, auth, middleware config
│   ├── urls.py                     # Root URL configuration
│   ├── wsgi.py
│   └── asgi.py
├── accounts/                       # Django app — Authentication
│   ├── __init__.py
│   ├── models.py                   # Custom User model (AbstractUser)
│   ├── forms.py                    # Login, Register forms
│   ├── views.py                    # Auth views (login, register, logout)
│   ├── urls.py
│   ├── admin.py
│   ├── decorators.py               # @admin_required, @student_required
│   └── templates/accounts/
│       ├── student_login.html
│       ├── student_register.html
│       └── tpo_login.html
├── students/                       # Django app — Student Portal
│   ├── __init__.py
│   ├── models.py                   # Student model
│   ├── forms.py                    # Profile, Resume forms
│   ├── views.py                    # Dashboard, profile, resume, drives
│   ├── urls.py
│   ├── admin.py
│   └── templates/students/
│       ├── dashboard.html
│       ├── profile.html
│       ├── upload_resume.html
│       └── drives.html
├── tpo/                            # Django app — TPO Admin Portal
│   ├── __init__.py
│   ├── models.py                   # Drive, Application models
│   ├── forms.py                    # Filter, Placement, Drive forms
│   ├── views.py                    # Dashboard, analytics, drives
│   ├── urls.py
│   ├── admin.py
│   ├── utils.py                    # CSV, ZIP generation, pagination
│   └── templates/tpo/
│       ├── dashboard.html
│       ├── student_detail.html
│       ├── analytics.html
│       └── drives/
│           ├── list.html
│           ├── create.html
│           └── applicants.html
├── core/                           # Shared app — Templates, static
│   ├── templates/
│   │   ├── base.html
│   │   ├── dashboard_base.html
│   │   └── home.html
│   └── templatetags/               # Custom template tags if needed
├── static/
│   ├── css/style.css
│   └── js/charts.js
└── media/
    └── resumes/                    # Uploaded PDFs (MEDIA_ROOT)
```

---

## 3. Component Mapping: Flask → Django

| Concern | Flask (Current) | Django (Target) |
|---------|-----------------|-----------------|
| App Factory | `create_app()` in `__init__.py` | `settings.py` + `INSTALLED_APPS` |
| Routing | `Blueprint` + `@bp.route()` | `urls.py` + `path()` per app |
| Views | Function-based views | Function-based views (or CBVs) |
| Models | Manual PyMongo classes | Django ORM models (`models.Model`) |
| Forms | Flask-WTF / WTForms | Django Forms (`forms.Form` / `ModelForm`) |
| Auth | Flask-Login + Flask-Bcrypt | Django's built-in `auth` + `AbstractUser` |
| CSRF | Flask-WTF `CSRFProtect` | Django middleware (built-in) |
| File Upload | `werkzeug.secure_filename` | Django `FileField` + `MEDIA_ROOT` |
| Session | Flask session + cookie | Django session framework (built-in) |
| Database | MongoDB (PyMongo) | MySQL 8.x (Django ORM) |
| Templates | Jinja2 | Django Template Language (compatible) |
| Admin Panel | None (manual) | Django Admin (auto-generated) |

---

## 4. Authentication & Authorization Flow

### 4.1 Custom User Model

We extend Django's `AbstractUser` to add a `role` field:

```python
class User(AbstractUser):
    ROLE_CHOICES = [('student', 'Student'), ('admin', 'Admin')]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')

    @property
    def is_admin(self):
        return self.role == 'admin'
```

### 4.2 Auth Flow

```
Student Register → Create User (role=student) + Create Student Profile → Redirect to Login
Student Login   → Authenticate → Check role=student → Create session → Redirect to Student Dashboard
TPO Login       → Authenticate → Check role=admin → Create session → Redirect to TPO Dashboard
Logout          → Flush session → Redirect to Home
```

### 4.3 Access Control Decorators

```python
# @admin_required — wraps @login_required, checks user.is_admin
# @student_required — wraps @login_required, checks NOT user.is_admin
```

---

## 5. Key Design Decisions

### 5.1 Why Django over Flask for production?
| Criterion | Flask | Django |
|-----------|-------|--------|
| ORM | None (manual queries) | Built-in, mature ORM |
| Admin Panel | Manual | Auto-generated |
| Auth System | Flask-Login (manual) | Built-in, battle-tested |
| Migrations | None | `makemigrations` / `migrate` |
| Security | Manual setup | CSRF, XSS, SQL injection baked in |
| Scalability | Micro-framework | Full-framework with middleware pipeline |

### 5.2 Why MySQL over MongoDB?
| Criterion | MongoDB (Current) | MySQL (Target) |
|-----------|-------------------|----------------|
| Schema | Schema-less | Strict schema with constraints |
| Relationships | Manual `$lookup` | Native JOINs, FK constraints |
| Data Integrity | Application-enforced | DB-enforced (constraints, cascades) |
| Indexing | Manual | Automatic via ORM + manual |
| Transactions | Limited | Full ACID compliance |
| Hosting | Requires Atlas / self-host | Widely available, cheap hosting |

### 5.3 File Storage Strategy
- Resumes stored in `MEDIA_ROOT/resumes/` directory
- Django's `FileField` handles upload, validation, and storage
- Files named as `{roll_no}_resume.pdf` for uniqueness
- Maximum file size enforced via `DATA_UPLOAD_MAX_MEMORY_SIZE`

---

## 6. Security Architecture

| Layer | Mechanism |
|-------|-----------|
| **Password Hashing** | Django's PBKDF2 (default) or Argon2 |
| **CSRF** | Django CSRF middleware (token in every POST form) |
| **Session** | Server-side, HTTP-only, SameSite=Lax cookies |
| **File Upload** | Extension whitelist (PDF), `FileExtensionValidator` |
| **SQL Injection** | Django ORM (parameterized queries) |
| **XSS** | Django template auto-escaping |
| **RBAC** | Custom decorators + Django permissions |
| **CORS** | Not needed (server-rendered, same-origin) |

---

## 7. Third-Party Dependencies

| Package | Purpose | Version |
|---------|---------|---------|
| `Django` | Web framework | 5.x |
| `mysqlclient` | MySQL connector | 2.x |
| `python-dotenv` | Env variable loading | 1.x |
| `Pillow` | Image processing (optional) | 10.x |
| `django-widget-tweaks` | Better form rendering | 1.x |

> **Note**: Django's built-in auth, forms, file handling, CSRF, and admin replace 5+ Flask extensions.

---

## 8. Deployment Considerations

| Aspect | Recommendation |
|--------|----------------|
| **WSGI Server** | Gunicorn behind Nginx |
| **Database** | MySQL 8.x (managed or self-hosted) |
| **Static Files** | `collectstatic` → served by Nginx / WhiteNoise |
| **Media Files** | Served by Nginx from `MEDIA_ROOT` |
| **Environment** | `.env` file with `python-dotenv` |
| **Migrations** | Version-controlled, run on deploy via `python manage.py migrate` |
