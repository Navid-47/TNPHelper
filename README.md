# TNPHelper — Resume Bank Management System

> A full-featured web portal for university Training & Placement Cells.
> Built with **Django 5.2 (LTS)**, **MySQL**, and **Bootstrap 5**.
> Requires **Python 3.11+**.

---

## 📋 Table of Contents

1. [Project Overview](#-project-overview)
2. [Key Features](#-key-features)
3. [Technology Stack](#-technology-stack)
4. [Architecture & Design](#-architecture--design)
5. [Database Schema](#-database-schema)
6. [Prerequisites](#-prerequisites)
7. [Installation & Setup](#-installation--setup)
8. [Running the Application](#-running-the-application)
9. [URL Map & Access Points](#-url-map--access-points)
10. [Sample Accounts](#-sample-accounts)
11. [Project Structure](#-project-structure)
12. [Application Modules (Detailed)](#-application-modules-detailed)
13. [UI/UX Design System](#-uiux-design-system)
14. [Key Workflows](#-key-workflows)
15. [Configuration Reference](#-configuration-reference)
16. [Data Export Capabilities](#-data-export-capabilities)
17. [Security Features](#-security-features)
18. [Troubleshooting](#-troubleshooting)
19. [Extending the Project](#-extending-the-project)
20. [Documentation Index](#-documentation-index)
21. [License](#-license)

---

## 🎯 Project Overview

The **Resume Bank Management System** is a web application designed for a university **Training & Placement Cell (TPO)**. It replaces manual spreadsheets and email-based resume collection with a centralized digital platform.

The system serves **two user roles**:

| Role | Portal | Purpose |
|------|--------|---------|
| **Student** | `/student/` | Register, maintain profile, upload resume (PDF), browse & apply to placement drives, track application status |
| **TPO Admin** | `/tpo/` | View student directory, filter/search/sort, download resumes (individual & bulk ZIP), export data to CSV, view analytics charts, create & manage placement drives, shortlist/reject/offer applicants |

---

## 🚀 Key Features

### Student Portal
- ✅ Student self-registration with automatic profile creation
- ✅ Dashboard with profile completion percentage
- ✅ Profile editing (name, roll number, branch, CGPA, skills)
- ✅ PDF resume upload & replacement (max 10 MB)
- ✅ Browse active placement drives
- ✅ One-click drive application (requires uploaded resume)
- ✅ "My Applications" page with real-time status tracking (Applied → Shortlisted → Offered / Rejected)

### TPO Admin Portal
- ✅ Paginated student directory (20 per page) with ellipsis pagination
- ✅ Advanced filtering: search by name/roll no, filter by branch, CGPA range, skills, placement status
- ✅ Sortable columns: name, roll no, CGPA, date (asc/desc)
- ✅ Individual student detail view with placement status update
- ✅ Individual resume download (PDF)
- ✅ Bulk resume download as ZIP archive
- ✅ CSV export of filtered student data
- ✅ Analytics dashboard with Chart.js visualizations:
  - CGPA distribution (bar chart)
  - Branch-wise student count
  - Placement rate (overall & per-branch)
  - Top 10 skills across all students
  - Average CGPA by branch
- ✅ Placement drive management (create, view, close)
- ✅ Applicant tracking per drive with shortlist/reject/offer actions

### General
- ✅ Custom landing page with feature showcase
- ✅ Role-based access control with custom decorators
- ✅ CSRF protection on all forms
- ✅ Mobile-responsive design (Bootstrap 5)
- ✅ Flash messages with auto-dismiss
- ✅ Custom 404 & 500 error pages

---

## 🛠 Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| **Backend Framework** | Django | 4.2.16 (LTS) |
| **Language** | Python | 3.10+ |
| **Database** | MySQL | 8.x (via XAMPP locally / Amazon RDS in prod) |
| **DB Connector** | mysqlclient | 2.2.4 |
| **Frontend** | HTML5, CSS3, JavaScript | — |
| **CSS Framework** | Bootstrap | 5.3 (CDN) |
| **Form Rendering** | django-crispy-forms + crispy-bootstrap5 | 2.3 / 2024.2 |
| **Charts** | Chart.js | CDN |
| **Template Engine** | Django Template Language (DTL) | Built-in |
| **Auth System** | Django's built-in auth | Extended with custom User model |
| **WSGI Server** | Gunicorn | 23.0 (production) |
| **Static Files** | WhiteNoise | 6.8 (production) |

### Python Dependencies (requirements.txt)

**Core packages:**

```
Django==4.2.16
mysqlclient==2.2.4
django-crispy-forms==2.3
crispy-bootstrap5==2024.2
```

**Production packages (included in requirements.txt):**

```
gunicorn==23.0.0        # WSGI server for AWS EC2
whitenoise==6.8.2       # Static file serving
python-decouple==3.8    # .env file support
```

All other functionality (CSV export, ZIP generation, file handling) uses Python's standard library.

---

## 🏗 Architecture & Design

The project follows Django's **multi-app architecture** pattern with clear separation of concerns:

```
┌─────────────────────────────────────────────────────┐
│                   resume_bank/                       │
│              (Project Configuration)                 │
│         settings.py · urls.py · wsgi.py              │
└─────────────┬───────────┬───────────┬───────────────┘
              │           │           │
    ┌─────────▼──┐  ┌─────▼─────┐  ┌─▼──────────┐
    │  accounts  │  │ students  │  │    tpo     │
    │ (Auth &    │  │ (Student  │  │ (Admin     │
    │  Users)    │  │  Portal)  │  │  Portal)   │
    └────────────┘  └───────────┘  └────────────┘
              │           │           │
              └─────────▼─┴───────────┘
                    ┌─────────┐
                    │  core   │
                    │(Landing │
                    │& Errors)│
                    └─────────┘
```

### Design Patterns Used

| Pattern | Implementation |
|---------|---------------|
| **Custom User Model** | `accounts.User` extends `AbstractUser` with a `role` field |
| **Role-Based Access** | `@admin_required` and `@student_required` decorators |
| **One-to-One Profile** | `Student` model linked to `User` via `OneToOneField` |
| **Atomic Transactions** | Registration creates `User` + `Student` in a single `transaction.atomic()` |
| **Reusable Filters** | `apply_student_filters()` utility shared across dashboard, CSV export, and bulk download |
| **Template Inheritance** | `base.html` → `dashboard_base.html` → page templates |

---

## 🗄 Database Schema

The application uses **4 models** across 3 apps:

### Entity Relationship

```
┌──────────────────┐       ┌──────────────────┐
│  accounts.User   │       │  students.Student │
│──────────────────│  1:1  │──────────────────│
│ username (email) │◄─────►│ name             │
│ password         │       │ roll_no (unique) │
│ role             │       │ email            │
│ first_name       │       │ branch           │
│ last_name        │       │ cgpa             │
│                  │       │ skills           │
│                  │       │ resume (FileField)│
│                  │       │ placement_status │
│                  │       │ company_name     │
│                  │       │ package          │
└──────────────────┘       └────────┬─────────┘
                                    │ 1:N
                                    ▼
                           ┌──────────────────┐
                           │  tpo.Application  │
                           │──────────────────│
                           │ student (FK)      │
         ┌──────────────┐  │ drive (FK)        │
         │  tpo.Drive    │  │ applied_at        │
         │──────────────│  │ status            │
         │ company_name │◄─┤ (unique_together  │
         │ role         │  │  drive+student)   │
         │ package      │  └──────────────────┘
         │ min_cgpa     │
         │ allowed_branches │
         │ backlogs_criteria│
         │ deadline     │
         │ status       │
         └──────────────┘
```

### Model Details

| Model | App | Key Fields | Notes |
|-------|-----|-----------|-------|
| `User` | accounts | username, email, password, **role** (student/admin) | Extends Django `AbstractUser` |
| `Student` | students | name, roll_no, email, branch, cgpa, skills, resume, placement_status, company_name, package | One-to-One with `User` |
| `Drive` | tpo | company_name, role, package, min_cgpa, allowed_branches, backlogs_criteria, deadline, status | Created by TPO admin |
| `Application` | tpo | drive (FK), student (FK), applied_at, status | Junction table; `unique_together = (drive, student)` |

### Status Enumerations

| Field | Values |
|-------|--------|
| `User.role` | `student`, `admin` |
| `Student.placement_status` | `not_placed`, `in_process`, `placed` |
| `Student.branch` | `CSE`, `ECE`, `EEE`, `ME`, `CE`, `IT`, `AI&DS` |
| `Drive.status` | `active`, `closed`, `completed` |
| `Drive.backlogs_criteria` | `any`, `no_active`, `no_history` |
| `Application.status` | `applied`, `shortlisted`, `rejected`, `offered` |

---

## 📋 Prerequisites

Before setting up, ensure you have:

| Requirement | Version | Purpose |
|-------------|---------|---------|
| **Python** | 3.10 or higher | Runtime |
| **pip** | Latest | Package manager |
| **XAMPP** | Any recent version | MySQL database server (local dev) |
| **Git** | Any | Version control |

> **Note for Windows users**: You may need the [Microsoft Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) installed for `mysqlclient` to compile.

> **AWS Deployment**: For production deployment on AWS EC2 + RDS, see [DEVOPS.md](DEVOPS.md).

---

## 🚀 Installation & Setup

### Step 1: Get the Project Files

```bash
# Option A — Clone from Git
git clone <repository-url>
cd TNPHelper

# Option B — Extract downloaded ZIP
# Unzip and navigate to the TNPHelper folder
```

### Step 2: Create a Virtual Environment

```bash
# Create
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up the Database

1. **Start XAMPP** → Ensure **Apache** and **MySQL** services are running
2. Open **phpMyAdmin**: http://localhost/phpmyadmin
3. Create a new database:
   - **Database name**: `tnp_db` ← **exact name used by the app**
   - Collation: `utf8mb4_general_ci`

> The database name, user, and password are configured in `resume_bank/settings.py`. The default configuration uses:
> - **Database**: `tnp_db`
> - **User**: `root`
> - **Password**: (empty)
> - **Host**: `localhost`
> - **Port**: `3306`

> **If you have a database dump** (e.g., `tnp_db.sql` included in the repo), you can import it directly in phpMyAdmin instead of running migrations. See [DEVOPS.md](DEVOPS.md#4-database-information) for import commands.

### Step 5: Run Migrations

```bash
python manage.py makemigrations accounts students tpo
python manage.py migrate
```

### Step 6: Load Sample Data (Optional but Recommended)

```bash
python setup.py
```

This creates:
- 1 admin user (TPO)
- 5 sample students with different branches, CGPAs, and placement statuses

### Step 7: Start the Development Server

```bash
python manage.py runserver
```

---

## 🌐 Running the Application

After starting the server, open your browser and visit:

```
http://127.0.0.1:8000/
```

You will see the landing page with links to both portals.

---

## 🗺 URL Map & Access Points

| URL | Page | Access |
|-----|------|--------|
| `/` | Landing Page | Public |
| `/auth/student/login/` | Student Login | Public |
| `/auth/student/register/` | Student Registration | Public |
| `/auth/student/logout/` | Student Logout | Student |
| `/auth/tpo/login/` | TPO Admin Login | Public |
| `/auth/tpo/logout/` | TPO Admin Logout | Admin |
| `/student/dashboard/` | Student Dashboard | Student |
| `/student/profile/` | Edit Profile | Student |
| `/student/upload-resume/` | Upload Resume | Student |
| `/student/download-resume/` | Download Own Resume | Student |
| `/student/drives/` | Browse Active Drives | Student |
| `/student/drives/<id>/apply/` | Apply to a Drive | Student |
| `/student/my-applications/` | My Applications | Student |
| `/tpo/dashboard/` | Student Directory | Admin |
| `/tpo/student/<id>/` | Student Detail & Status Update | Admin |
| `/tpo/analytics/` | Analytics Dashboard | Admin |
| `/tpo/export/csv/` | CSV Export | Admin |
| `/tpo/download-resume/<id>/` | Download Student Resume | Admin |
| `/tpo/bulk-download-resumes/` | Bulk Download (ZIP) | Admin |
| `/tpo/drives/` | Drives List | Admin |
| `/tpo/drives/create/` | Create New Drive | Admin |
| `/tpo/drives/<id>/applicants/` | View Drive Applicants | Admin |
| `/tpo/applications/<id>/update-status/` | Update Application Status | Admin |
| `/admin/` | Django Admin Panel | Superuser |

---

## 👥 Sample Accounts

Created by running `python setup.py`:

### TPO Admin
| Field | Value |
|-------|-------|
| Username | `admin` |
| Password | `admin123` |

### Sample Students

| Name | Email (Username) | Password | Branch | CGPA | Status |
|------|-----------------|----------|--------|------|--------|
| John Doe | `student1@example.com` | `student123` | CSE | 8.50 | Placed (Tech Corp, 12.5 LPA) |
| Jane Smith | `student2@example.com` | `student123` | ECE | 9.20 | Placed (Electronics Inc, 15.0 LPA) |
| Mike Johnson | `student3@example.com` | `student123` | ME | 7.80 | In Process |
| Sarah Wilson | `student4@example.com` | `student123` | CSE | 8.90 | Not Placed |
| David Brown | `student5@example.com` | `student123` | IT | 8.10 | Placed (Data Analytics Ltd, 14.0 LPA) |

---

## 📁 Project Structure

```
TNPHelper/
│
├── manage.py                    # Django management CLI
├── requirements.txt             # Python dependencies
├── setup.py                     # Sample data seeder script
├── .gitignore                   # Git ignore rules
├── tnp_db.sql                   # MySQL database dump (import into tnp_db)
│
├── resume_bank/                 # ── Django Project Configuration ──
│   ├── __init__.py
│   ├── settings.py              # Database, apps, auth, static/media config
│   ├── urls.py                  # Root URL routing (includes all app URLs)
│   └── wsgi.py                  # WSGI entry point for deployment
│
├── accounts/                    # ── Authentication & User Management ──
│   ├── models.py                # Custom User model (AbstractUser + role)
│   ├── views.py                 # Login, register, logout views
│   ├── forms.py                 # Registration & login forms
│   ├── decorators.py            # @admin_required, @student_required
│   ├── admin.py                 # Django admin configuration
│   ├── urls.py                  # Auth URL patterns (/auth/...)
│   └── migrations/              # Database migrations
│
├── students/                    # ── Student Portal ──
│   ├── models.py                # Student model (profile, resume, placement)
│   ├── views.py                 # Dashboard, profile, resume, drives views
│   ├── forms.py                 # Profile edit & resume upload forms
│   ├── admin.py                 # Django admin for Student model
│   ├── urls.py                  # Student URL patterns (/student/...)
│   └── migrations/              # Database migrations
│
├── tpo/                         # ── TPO Admin Portal ──
│   ├── models.py                # Drive & Application models
│   ├── views.py                 # Dashboard, analytics, drives, exports
│   ├── forms.py                 # Filter, status update, drive forms
│   ├── utils.py                 # Shared filter logic (apply_student_filters)
│   ├── admin.py                 # Django admin for Drive/Application
│   ├── urls.py                  # TPO URL patterns (/tpo/...)
│   └── migrations/              # Database migrations
│
├── core/                        # ── Shared / Public Pages ──
│   ├── views.py                 # Landing page, 404, 500 handlers
│   ├── urls.py                  # Root URL pattern (/)
│   └── apps.py                  # App configuration
│
├── templates/                   # ── HTML Templates ──
│   ├── base.html                # Root template (head, meta, Bootstrap CDN)
│   ├── dashboard_base.html      # Sidebar layout for authenticated users
│   ├── home.html                # Public landing page
│   ├── 404.html                 # Custom "Not Found" page
│   ├── 500.html                 # Custom "Server Error" page
│   ├── accounts/                # Login & registration templates
│   │   ├── student_login.html
│   │   ├── student_register.html
│   │   └── tpo_login.html
│   ├── students/                # Student portal templates
│   │   ├── dashboard.html
│   │   ├── profile.html
│   │   ├── upload_resume.html
│   │   ├── drives.html
│   │   └── my_applications.html
│   └── tpo/                     # TPO admin templates
│       ├── dashboard.html
│       ├── student_detail.html
│       ├── analytics.html
│       └── drives/
│           ├── list.html
│           ├── create.html
│           └── applicants.html
│
├── static/                      # ── Static Assets ──
│   ├── css/
│   │   └── style.css            # Custom CSS (design system)
│   └── favicon.svg              # Site favicon
│
├── media/                       # ── Uploaded Files (gitignored) ──
│   └── resumes/                 # Student resume PDFs
│
├── docs/                        # ── Project Documentation ──
│   ├── 01_PRD.md                # Product Requirements Document
│   ├── 02_System_Design_Document.md
│   ├── 03_Database_Design.md
│   ├── 04_API_Specification.md
│   ├── 05_Django_Migration_Guide.md
│   └── 06_UI_Design_Document.md
│
├── DEVOPS.md                    # AWS deployment guide (EC2, RDS, Nginx, Gunicorn)
├── project_architecture.md      # Architecture overview
├── QUICK_START.md               # Quick setup guide
└── README.md                    # This file
```

---

## 📦 Application Modules (Detailed)

### A. `accounts` — Authentication & Access Control

**Purpose**: Manages user registration, login/logout, and role-based access.

| File | Responsibility |
|------|---------------|
| `models.py` | Custom `User` model extending `AbstractUser` with `role` field (`student` / `admin`). Properties: `is_admin`, `is_student`. |
| `views.py` | 4 views: `student_register`, `student_login`, `student_logout`, `tpo_login` / `tpo_logout`. Uses `transaction.atomic()` for safe registration. |
| `forms.py` | `StudentRegistrationForm` (extends `UserCreationForm`, creates User + Student together), `StudentLoginForm`, `TPOLoginForm`. |
| `decorators.py` | `@admin_required` — blocks non-admin users. `@student_required` — blocks non-student users. Both wrap Django's `@login_required`. |

### B. `students` — Student Portal

**Purpose**: Handles everything related to a student's profile and placement activities.

| File | Responsibility |
|------|---------------|
| `models.py` | `Student` model: OneToOneField → User, personal info, academic info (branch, CGPA), skills (comma-separated), resume (FileField → `media/resumes/`), placement status. Helper methods: `get_skills_list()`, `get_profile_completion()`, `get_resume_filename()`. |
| `views.py` | 7 views: `student_dashboard`, `student_profile`, `upload_resume`, `download_resume`, `drives_list`, `apply_drive`, `my_applications`. All protected with `@student_required`. |
| `forms.py` | `StudentProfileForm` (edit profile), `ResumeUploadForm` (PDF upload with file validation). |

### C. `tpo` — TPO Administrator Portal

**Purpose**: Student tracking, analytics, data export, and placement drive management.

| File | Responsibility |
|------|---------------|
| `models.py` | `Drive` (placement drive with eligibility criteria) and `Application` (junction table linking Student ↔ Drive with status tracking). |
| `views.py` | 9 views: `tpo_dashboard` (directory), `student_detail`, `tpo_analytics`, `download_resume`, `export_csv`, `bulk_download_resumes`, `drives_list`, `create_drive`, `drive_applicants`, `update_app_status`. All protected with `@admin_required`. |
| `forms.py` | `StudentFilterForm`, `PlacementStatusUpdateForm`, `DriveForm`, `ApplicationStatusForm`. |
| `utils.py` | `apply_student_filters()` — reusable filtering logic shared by dashboard, CSV export, and bulk download. |

### D. `core` — Public Pages

**Purpose**: Lightweight app for the landing page and error handlers.

| File | Responsibility |
|------|---------------|
| `views.py` | `home` (landing page), `custom_404`, `custom_500`. |

---

## 🎨 UI/UX Design System

| Aspect | Implementation |
|--------|---------------|
| **CSS Framework** | Bootstrap 5.3 (loaded via CDN) |
| **Custom Styles** | `static/css/style.css` — Teal & Slate color palette |
| **Design Style** | Glassmorphism (blur-backed glass panels), soft shadows |
| **Layout** | Sidebar navigation (`dashboard_base.html`) — dynamically shows/hides links based on user role |
| **Interactivity** | Auto-dismissing flash messages, double-submit protection with "Processing…" spinner |
| **Status Badges** | Dynamic CSS classes: `.status-shortlisted` (blue), `.status-offered` (green), `.status-rejected` (red) |
| **Charts** | Chart.js — bar, pie, and doughnut charts on the analytics page |
| **Responsive** | Mobile-first grid. Sidebar collapses to hamburger menu on small screens. |

---

## 🔄 Key Workflows

### Student Registration & Setup

```
1. Student → /auth/student/register/
2. Form creates User (role=student) + Student profile (transaction.atomic)
3. Student logs in → /student/dashboard/
4. Dashboard shows Profile Completion % → prompts to upload resume
5. Student uploads PDF → saved as media/resumes/{roll_no}_resume.pdf
```

### Drive Application Flow

```
1. TPO Admin creates an "Active" drive → /tpo/drives/create/
2. Student sees it on "Browse Drives" page → /student/drives/
3. Student clicks "Apply" → system checks if resume exists
4. Application record created (status = "Applied")
5. TPO Admin views applicants → /tpo/drives/{id}/applicants/
6. TPO clicks Shortlist / Reject / Offer
7. Student checks "My Applications" → sees updated status badge
```

### Data Export Flow

```
1. TPO sets filters on dashboard (branch, CGPA, status, etc.)
2. Clicks "Export CSV" → downloads filtered students_data.csv
3. Or clicks "Download All Resumes" → downloads student_resumes.zip
```

---

## ⚙ Configuration Reference

All configuration is in `resume_bank/settings.py`:

### Database

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'tnp_db',           # ← Change database name here
        'USER': 'root',              # ← Change MySQL username
        'PASSWORD': '',              # ← Change MySQL password
        'HOST': 'localhost',         # ← Change host if remote
        'PORT': '3306',              # ← Change port if non-default
    }
}
```

### File Upload

| Setting | Value |
|---------|-------|
| Upload directory | `media/resumes/` |
| Max file size | 10 MB |
| Allowed extensions | `.pdf` only |
| File naming | `{roll_no}_resume.pdf` |

### Authentication

| Setting | Value |
|---------|-------|
| `LOGIN_URL` | `/auth/student/login` |
| `LOGIN_REDIRECT_URL` | `/student/dashboard` |
| `LOGOUT_REDIRECT_URL` | `/` |
| `AUTH_USER_MODEL` | `accounts.User` |

### Crispy Forms

| Setting | Value |
|---------|-------|
| `CRISPY_TEMPLATE_PACK` | `bootstrap5` |

---

## 📊 Data Export Capabilities

| Export Type | Format | Access | Filtered? |
|-------------|--------|--------|-----------|
| Student Directory | CSV (.csv) | TPO Admin | ✅ Yes — respects active filters |
| Individual Resume | PDF | TPO Admin | N/A |
| Bulk Resumes | ZIP (.zip) | TPO Admin | ✅ Yes — respects active filters |

**CSV columns**: Roll No, Name, Email, Branch, CGPA, Skills, Status, Company, Package, Has Resume.

---

## 🔒 Security Features

| Feature | Implementation |
|---------|---------------|
| **Password Hashing** | Django's PBKDF2 (default) |
| **CSRF Protection** | Django middleware + `{% csrf_token %}` in all forms |
| **Role-Based Access** | Custom `@admin_required` and `@student_required` decorators |
| **File Upload Validation** | Extension check (PDF only), size limit (10 MB) |
| **Session Security** | Django's session framework with database-backed sessions |
| **XSS Prevention** | Django's auto-escaping in templates |
| **SQL Injection Prevention** | Django ORM (parameterized queries) |
| **Unique Constraints** | `roll_no` is unique; `(drive, student)` unique_together prevents duplicate applications |

---

## 🐛 Troubleshooting

### 1. Database Connection Error
```
django.db.utils.OperationalError: (2003, "Can't connect to MySQL server")
```
**Fix**: Start XAMPP → ensure MySQL service is running. Verify database `tnp_db` exists in phpMyAdmin.

### 2. `mysqlclient` Installation Fails
```
error: Microsoft Visual C++ 14.0 or greater is required.
```
**Fix (Windows)**: Install [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/). Alternatively, install `PyMySQL` as a drop-in replacement:
```bash
pip install PyMySQL
```
Then add to `resume_bank/__init__.py`:
```python
import pymysql
pymysql.install_as_MySQLdb()
```

### 3. Migration Errors
```
django.db.utils.ProgrammingError: Table already exists
```
**Fix**: Reset migrations:
```bash
# Delete migration files (keep __init__.py)
del accounts\migrations\0*.py
del students\migrations\0*.py
del tpo\migrations\0*.py

# Recreate
python manage.py makemigrations accounts students tpo
python manage.py migrate
```

### 4. Static Files Not Loading

**Fix**:
```bash
python manage.py collectstatic
```
Also verify `STATIC_URL` and `STATICFILES_DIRS` are set correctly in `settings.py`.

### 5. File Upload Issues

**Fix**: Ensure the `media/` directory exists and is writable. Django creates `media/resumes/` automatically on first upload.

### 6. "No student profile found" After Login

**Fix**: The user account exists but has no linked `Student` record. This happens if registration failed partway. Delete the orphaned user from Django admin (`/admin/`) and re-register.

---

## 🔧 Extending the Project

### Adding a New Field to Student Profile

1. Add field in `students/models.py`
2. Add field to the form in `students/forms.py`
3. Run migrations:
   ```bash
   python manage.py makemigrations students
   python manage.py migrate
   ```
4. Update templates to display the new field

### Adding a New Branch

Edit `BRANCH_CHOICES` in `students/models.py`:
```python
BRANCH_CHOICES = [
    ('CSE', 'Computer Science Engineering'),
    # ... existing branches ...
    ('BT', 'Biotechnology'),  # ← Add new branch
]
```
Then run migrations.

### Switching to SQLite (No XAMPP Needed)

Replace the `DATABASES` setting in `resume_bank/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```
Then run migrations. No `mysqlclient` dependency needed.

---

## 📚 Documentation Index

Detailed design documents are available in the `docs/` folder:

| Document | Description |
|----------|-------------|
| [01_PRD.md](docs/01_PRD.md) | Product Requirements Document — goals, user personas, feature matrix |
| [02_System_Design_Document.md](docs/02_System_Design_Document.md) | System architecture, component design |
| [03_Database_Design.md](docs/03_Database_Design.md) | Detailed schema, relationships, constraints |
| [04_API_Specification.md](docs/04_API_Specification.md) | URL/view specification |
| [05_Django_Migration_Guide.md](docs/05_Django_Migration_Guide.md) | Migration strategy and notes |
| [06_UI_Design_Document.md](docs/06_UI_Design_Document.md) | UI/UX design specifications, wireframes |
| [project_architecture.md](project_architecture.md) | Architecture overview |
| [QUICK_START.md](QUICK_START.md) | Quick 5-minute setup guide |
| [DEVOPS.md](DEVOPS.md) | **AWS deployment guide** — EC2, RDS, Nginx, Gunicorn, S3 |

---

## 📄 License

This project is developed for educational purposes as part of a university engineering curriculum.

---

## 🤝 Developer-DevOps Contract

> This section is the authoritative reference for the hand-off between the application developer and the DevOps/infrastructure team.

### Python & Django versions

| Component | Version |
|---|---|
| Python | **3.11 or 3.12** (3.10 and 3.13 also supported by Django 5.2) |
| Django | **5.2.18** (LTS — supported until April 2028) |
| WSGI server | gunicorn 23.x |

### Required environment variables

All variables below must be present in the process environment before the app starts.
See [`.env.example`](.env.example) for the complete list with descriptions.

| Variable | Required in prod? | Description |
|---|---|---|
| `SECRET_KEY` | **Yes — app refuses to start without it** | Long random Django secret key |
| `DEBUG` | Yes (set `False`) | Must be `False` in production |
| `ALLOWED_HOSTS` | Yes | Comma-separated hostnames (no `*`) |
| `CSRF_TRUSTED_ORIGINS` | Yes (HTTPS) | Comma-separated origins with scheme |
| `DB_NAME` | Yes | MySQL database name |
| `DB_USER` | Yes | MySQL username (not root) |
| `DB_PASSWORD` | Yes | MySQL password |
| `DB_HOST` | Yes | MySQL host / RDS endpoint |
| `DB_PORT` | Yes | MySQL port (usually `3306`) |
| `MAX_RESUME_SIZE` | No (default 5 MB) | Max resume upload size in bytes |
| `SECURE_SSL_REDIRECT` | No (default `True`) | Set `False` if Nginx handles redirects |
| `SECURE_HSTS_SECONDS` | No (default 31536000) | HSTS duration |
| `SESSION_COOKIE_SECURE` | No (default `True`) | Must be `True` behind HTTPS |
| `CSRF_COOKIE_SECURE` | No (default `True`) | Must be `True` behind HTTPS |

### Health endpoint

```
GET /healthz/          → 200 {"status": "ok"}   (shallow, no DB)
GET /healthz/?deep=1   → 200 {"status": "ok"}   (pings DB with SELECT 1)
                        → 503 {"status": "error"} (DB unreachable)
```

- No authentication required
- No CSRF required
- Returns JSON; Content-Type: application/json
- Safe to expose to load balancer health checks

### Deployment commands (run as the app user)

```bash
# 1. Install dependencies (requires system packages for mysqlclient — see below)
pip install -r requirements.txt

# 2. Apply database migrations (NEVER run makemigrations in deploy)
python manage.py migrate --noinput

# 3. Collect static files
python manage.py collectstatic --noinput

# 4. Start Gunicorn
gunicorn resume_bank.wsgi:application --bind unix:/run/gunicorn.sock
```

### System packages required for mysqlclient

```bash
# Ubuntu / Debian
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential pkg-config

# Amazon Linux 2 / RHEL
sudo yum install mysql-devel gcc python3-devel
```

### CI gate

Add this to your CI pipeline to prevent secrets being committed:

```bash
python scripts/check_repo_clean.py
```

Exits 1 if any `.sql`, `.pdf`, `.env`, `.pem`, `.key` or other forbidden file types are tracked in Git.

### Static and media files

| Type | Location | Served by |
|---|---|---|
| Static (CSS/JS) | `staticfiles/` (after `collectstatic`) | Nginx directly |
| Media (resumes) | `media/resumes/` | **NOT public** — Django authenticated views only |

> ⚠️ **Nginx must NOT add a public alias for `media/`.** Resume files are served exclusively through authenticated Django views that enforce ownership checks.

### WSGI entry point

```
resume_bank.wsgi:application
```

---

**Happy Coding! 🚀**
