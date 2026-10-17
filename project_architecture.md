# TNPHelper — Project Architecture & Technical Documentation

> A deep-dive into the technical design, data flow, and implementation details of the Resume Bank Management System.

---

## 1. System Overview

TNPHelper is a **Resume Bank Management System** designed for a university Training & Placement Cell (TPO). It is built using the **Django 3.2 LTS** web framework (Python) with a **MySQL** database backend (served via XAMPP). The application features a split portal system: one for **Students** and one for **TPO Administrators**.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       Client (Browser)                       │
│                  Bootstrap 5 · Chart.js · JS                 │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP (GET/POST)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     Django Application                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ accounts │  │ students │  │   tpo    │  │   core   │    │
│  │  (Auth)  │  │ (Portal) │  │ (Admin)  │  │ (Public) │    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │
│       │              │              │              │          │
│       └──────────────┴──────────────┴──────────────┘          │
│                           │                                   │
│                  Django ORM (Models)                          │
└──────────────────────────┬──────────────────────────────────┘
                           │ SQL
                           ▼
               ┌──────────────────────┐
               │   MySQL (XAMPP)      │
               │   Database: tnp_db   │
               └──────────────────────┘
```

---

## 2. Django App Architecture

The project is organized as a **multi-app Django project** with 4 apps plus the configuration module:

```
TNPHelper/
├── manage.py               # Django management CLI
├── resume_bank/            # Project configuration (settings, root URLs, WSGI)
│   ├── settings.py         # All configuration (DB, apps, auth, static, media)
│   ├── urls.py             # Root URL router — delegates to app URLs
│   └── wsgi.py             # WSGI entry point
├── accounts/               # App 1: Authentication & User Management
├── students/               # App 2: Student Portal
├── tpo/                    # App 3: TPO Admin Portal
├── core/                   # App 4: Public Pages (landing, errors)
├── templates/              # All HTML templates
├── static/                 # CSS, favicon
└── media/                  # Uploaded resume files
```

### App Dependency Graph

```
accounts  ←── students (imports Student model in forms)
    ↑              ↑
    │              │
    └── tpo ───────┘ (imports Student model, uses decorators)
         │
    core (standalone — no model dependencies)
```

---

## 3. Application Modules — Detailed Breakdown

### A. `accounts` (Authentication & Access Control)

**Handles**: Custom user model, login, registration, role management.

#### Custom User Model (`models.py`)
- Extends Django's `AbstractUser` to add a `role` field:
  - `role='student'` — Standard student accounts
  - `role='admin'` — TPO administrator accounts
- Properties: `is_admin` and `is_student` for clean role checks in templates and views
- Registered as `AUTH_USER_MODEL = 'accounts.User'` in settings

#### Authentication Views (`views.py`)
| View | URL | Method | Purpose |
|------|-----|--------|---------|
| `student_register` | `/auth/student/register/` | GET/POST | Creates User (role=student) + Student profile atomically |
| `student_login` | `/auth/student/login/` | GET/POST | Authenticates, verifies role=student, checks profile exists |
| `student_logout` | `/auth/student/logout/` | GET | Logs out, redirects to home |
| `tpo_login` | `/auth/tpo/login/` | GET/POST | Authenticates, verifies role=admin |
| `tpo_logout` | `/auth/tpo/logout/` | GET | Logs out, redirects to home |

#### Registration Atomicity
The registration view uses `transaction.atomic()` to ensure the `User` and `Student` records are created together. If either fails, both are rolled back — preventing orphaned user accounts.

#### Custom Decorators (`decorators.py`)
| Decorator | Behavior |
|-----------|----------|
| `@admin_required` | Wraps `@login_required` → checks `request.user.is_admin` → redirects to home with error message if unauthorized |
| `@student_required` | Wraps `@login_required` → checks `request.user.is_student` → redirects with error if unauthorized |

---

### B. `students` (Student Portal)

**Handles**: Dashboard, profile management, resume upload/download, drive browsing, and applications.

#### Student Model (`models.py`)
- **Relationship**: `OneToOneField` → `accounts.User` (related_name: `student_profile`)
- **File Upload**: `FileField` with custom upload path `media/resumes/{roll_no}_resume.pdf`
- **Key Helper Methods**:

| Method | Returns | Purpose |
|--------|---------|---------|
| `get_skills_list()` | `['Python', 'Java', ...]` | Splits comma-separated skills string |
| `get_profile_completion()` | `{'percentage': 85, 'missing': [...]}` | Calculates how complete the profile is (7 fields checked) |
| `get_resume_filename()` | `'2021001_resume.pdf'` | Extracts just the filename from the FileField |
| `get_branch_display_name()` | `'Computer Science Engineering'` | Maps branch code to full name |
| `is_placed()` | `True/False` | Checks if `placement_status == 'placed'` |

#### Student Views (`views.py`)

| View | Purpose | Key Logic |
|------|---------|-----------|
| `student_dashboard` | Main dashboard | Loads profile completion %, skills list |
| `student_profile` | Edit profile | ModelForm (StudentProfileForm) |
| `upload_resume` | Upload PDF | Deletes old file before saving new one |
| `download_resume` | Download own resume | Serves file with `content_type='application/pdf'` |
| `drives_list` | Browse active drives | Annotates drives with student's application status |
| `apply_drive` | Apply to drive | Checks resume exists, prevents duplicate applications |
| `my_applications` | View all applications | Shows all with `select_related('drive')` for efficiency |

---

### C. `tpo` (TPO Admin Portal)

**Handles**: Student directory, analytics, data export, placement drive lifecycle.

#### Models (`models.py`)

**Drive Model**:
- Represents a campus recruitment drive
- Eligibility: `min_cgpa`, `allowed_branches` (comma-separated), `backlogs_criteria`
- Lifecycle: `status` — Active → Closed → Completed

**Application Model**:
- Junction table: `student` (FK) ↔ `drive` (FK)
- `unique_together = ('drive', 'student')` — prevents duplicate applications
- Status progression: Applied → Shortlisted → Offered -or- → Rejected

#### TPO Views (`views.py`)

| View | Purpose | Key Logic |
|------|---------|-----------|
| `tpo_dashboard` | Student directory | Filter form + pagination (20/page) + ellipsis range |
| `student_detail` | View/update student | PlacementStatusUpdateForm for status changes |
| `tpo_analytics` | Charts & statistics | CGPA distribution, branch stats, placement rate, top skills, avg CGPA |
| `download_resume` | Download one resume | Serves PDF file |
| `export_csv` | CSV export | Respects current filters; columns: Roll No, Name, Email, Branch, CGPA, Skills, Status, Company, Package, Has Resume |
| `bulk_download_resumes` | ZIP download | Creates in-memory ZIP of all filtered students' resumes |
| `drives_list` | List all drives | Shows drive info + applicant count |
| `create_drive` | Create new drive | DriveForm with eligibility criteria |
| `drive_applicants` | View applicants | Lists all applications for a drive |
| `update_app_status` | Update application | Changes status (shortlist/reject/offer) |

#### Reusable Filter Utility (`utils.py`)

`apply_student_filters(queryset, form)` is shared across 3 views:
- `tpo_dashboard` — for displaying filtered results
- `export_csv` — for exporting filtered data
- `bulk_download_resumes` — for downloading filtered resumes

**Filter capabilities**:
1. Search (name or roll number — case-insensitive)
2. Branch filter (exact match)
3. CGPA range (min/max)
4. Skills filter (all specified skills must match — AND logic)
5. Placement status filter
6. Sort by (name, roll_no, cgpa, created_at — asc/desc)

---

### D. `core` (Public Pages)

**Handles**: Landing page and custom error pages.

| View | URL | Purpose |
|------|-----|---------|
| `home` | `/` | Public landing page with feature showcase |
| `custom_404` | (auto) | Custom "Page Not Found" error page |
| `custom_500` | (auto) | Custom "Internal Server Error" page |

---

## 4. Template Inheritance Hierarchy

```
base.html                          ← Root (head, meta, Bootstrap CDN, favicon)
├── home.html                      ← Landing page (public)
├── accounts/student_login.html    ← Student login
├── accounts/student_register.html ← Student registration
├── accounts/tpo_login.html        ← TPO login
├── 404.html                       ← Error page
├── 500.html                       ← Error page
│
└── dashboard_base.html            ← Sidebar layout (authenticated users)
    ├── students/dashboard.html
    ├── students/profile.html
    ├── students/upload_resume.html
    ├── students/drives.html
    ├── students/my_applications.html
    ├── tpo/dashboard.html
    ├── tpo/student_detail.html
    ├── tpo/analytics.html
    ├── tpo/drives/list.html
    ├── tpo/drives/create.html
    └── tpo/drives/applicants.html
```

### Sidebar Navigation

`dashboard_base.html` renders different sidebar links based on `request.user`:
- **Student sidebar**: Dashboard, Profile, Upload Resume, Browse Drives, My Applications, Logout
- **Admin sidebar**: Dashboard, Analytics, Manage Drives, Logout

---

## 5. Request Flow (Example: Student applies to a drive)

```
1. Student clicks "Apply" button on /student/drives/
   └── POST /student/drives/5/apply/

2. Django URL Router (students/urls.py)
   └── Matches: path('drives/<int:drive_id>/apply/', views.apply_drive)

3. Decorator: @student_required
   ├── @login_required checks session → user is authenticated ✓
   └── Checks request.user.is_student → True ✓

4. View: apply_drive(request, drive_id=5)
   ├── Gets student profile: request.user.student_profile
   ├── Gets drive: Drive.objects.get(id=5, status='active')
   ├── Checks student.resume exists → True ✓
   ├── Checks duplicate: Application.objects.filter(drive=5, student=X).exists() → False ✓
   └── Creates: Application(drive=drive, student=student, status='applied')

5. Response: redirect('students:drives_list')
   └── Flash message: "Successfully applied to TechCorp - SDE!"

6. Student sees updated drives page with "Applied" badge next to that drive
```

---

## 6. Analytics Engine (tpo/views.py → tpo_analytics)

The analytics dashboard computes the following metrics in a single view:

| Metric | Query | Chart Type |
|--------|-------|------------|
| CGPA Distribution | 5 range-filtered counts (9-10, 8-8.99, etc.) | Bar chart |
| Branch Distribution | `values('branch').annotate(count=Count('id'))` | Doughnut chart |
| Placement Statistics | 3 status-filtered counts | Pie chart |
| Top 10 Skills | Python `Counter` on all students' skills | Horizontal bar |
| Avg CGPA by Branch | `values('branch').annotate(avg_cgpa=Avg('cgpa'))` | Bar chart |
| Branch-wise Placement Rate | Manual loop: placed_count / branch_total × 100 | Table |

All data is passed to the template and rendered client-side using **Chart.js**.

---

## 7. File Storage Architecture

```
TNPHelper/
└── media/
    └── resumes/
        ├── 2021001_resume.pdf    ← student_resume_path() generates this
        ├── 2021002_resume.pdf
        └── ...
```

- **Upload path function**: `student_resume_path(instance, filename)` in `students/models.py`
- **Naming convention**: `{roll_no}_resume.{ext}` — prevents file collisions
- **Old file cleanup**: `upload_resume` view deletes the old file before saving the new one
- **Serving**: Files are served via `MEDIA_URL` in development (Django's static file handler)

---

## 8. Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| Django | 3.2.24 | Web framework (views, ORM, auth, templates, admin) |
| mysqlclient | 2.2.0 | MySQL database connector (C extension for performance) |
| django-crispy-forms | 1.14.0 | Render Django forms with Bootstrap styling |
| crispy-bootstrap5 | 0.7 | Bootstrap 5 template pack for crispy-forms |

**Standard library modules used** (no install needed): `csv`, `zipfile`, `os`, `collections.Counter`

**Frontend CDNs** (no npm/node needed):
- Bootstrap 5.3 (CSS + JS)
- Chart.js (analytics charts)
- Bootstrap Icons (sidebar & badge icons)

---

*For setup instructions, see [README.md](README.md) or [QUICK_START.md](QUICK_START.md).*
