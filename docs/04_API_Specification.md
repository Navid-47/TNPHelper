# API & Route Specification
## Resume Bank Management System — URL Endpoints

| Field | Value |
|-------|-------|
| **Date** | 2026-02-13 |
| **Framework** | Django 5.x (server-rendered, no REST API) |
| **Auth** | Session-based (Django auth) |

---

## 1. URL Namespace Overview

| App | URL Prefix | Namespace |
|-----|-----------|-----------|
| Core | `/` | `core` |
| Accounts | `/auth/` | `accounts` |
| Students | `/student/` | `students` |
| TPO | `/tpo/` | `tpo` |

---

## 2. Core Routes

| Method | URL | View Name | Auth | Description |
|--------|-----|-----------|------|-------------|
| GET | `/` | `core:home` | None | Landing page with hero, features, portal links |

---

## 3. Account Routes (`/auth/`)

| Method | URL | View Name | Auth | Description |
|--------|-----|-----------|------|-------------|
| GET, POST | `/auth/student/register` | `accounts:student_register` | None | Student registration form |
| GET, POST | `/auth/student/login` | `accounts:student_login` | None | Student login form |
| GET | `/auth/student/logout` | `accounts:student_logout` | Student | Logout + redirect home |
| GET, POST | `/auth/tpo/login` | `accounts:tpo_login` | None | TPO admin login form |
| GET | `/auth/tpo/logout` | `accounts:tpo_logout` | Admin | Logout + redirect home |

### Registration Flow
```
POST /auth/student/register
Body (form):
  - email: str (required, unique)
  - password: str (required, min 8 chars)
  - confirm_password: str (must match)
  - name: str (required, max 100)
  - roll_no: str (required, max 20, unique)
  - branch: str (from BRANCH_CHOICES)
  - cgpa: decimal (0.0 - 10.0)
  - skills: str (comma-separated)

Success: Redirect → /auth/student/login (flash: "Registration successful!")
Failure: Re-render form with validation errors
```

### Login Flow
```
POST /auth/student/login
Body (form):
  - email: str (required)
  - password: str (required)

Success: Redirect → /student/dashboard
Failure: Re-render form (flash: "Invalid email or password")
```

---

## 4. Student Routes (`/student/`)

All routes require `@login_required` + `@student_required`

| Method | URL | View Name | Description |
|--------|-----|-----------|-------------|
| GET | `/student/dashboard` | `students:dashboard` | Profile card, resume status, placement info |
| GET, POST | `/student/profile` | `students:profile` | Edit profile form |
| GET, POST | `/student/upload-resume` | `students:upload_resume` | Resume PDF upload |
| GET | `/student/download-resume` | `students:download_resume` | Download own resume file |
| GET | `/student/drives` | `students:drives_list` | List active placement drives |
| POST | `/student/drives/<drive_id>/apply` | `students:apply_drive` | Apply to a drive |

### Profile Update
```
POST /student/profile
Body (form):
  - name: str
  - branch: str
  - cgpa: decimal
  - skills: str (comma-separated)
  - placement_status: str (not_placed | in_process | placed)
  - company_name: str (if placed)
  - package: decimal (if placed)

Success: Redirect → /student/dashboard
```

### Resume Upload
```
POST /student/upload-resume
Body (multipart):
  - resume: File (PDF only, max 10MB)

Success: Redirect → /student/dashboard
Validation: PDF extension only, max 10MB
```

---

## 5. TPO Routes (`/tpo/`)

All routes require `@login_required` + `@admin_required`

| Method | URL | View Name | Description |
|--------|-----|-----------|-------------|
| GET | `/tpo/dashboard` | `tpo:dashboard` | Student directory with filters |
| GET | `/tpo/analytics` | `tpo:analytics` | Charts dashboard |
| GET, POST | `/tpo/student/<id>` | `tpo:student_detail` | View/update student placement |
| GET | `/tpo/download-resume/<id>` | `tpo:download_resume` | Download student resume |
| GET | `/tpo/export-csv` | `tpo:export_csv` | Export filtered data as CSV |
| GET | `/tpo/bulk-download` | `tpo:bulk_download` | Download filtered resumes as ZIP |
| GET | `/tpo/drives` | `tpo:drives_list` | List all placement drives |
| GET, POST | `/tpo/drives/create` | `tpo:create_drive` | Create new drive |
| GET | `/tpo/drives/<id>/applicants` | `tpo:drive_applicants` | View drive applicants |
| POST | `/tpo/drives/application/<id>/status` | `tpo:update_app_status` | Update application status |

### Dashboard Filter Query Params
```
GET /tpo/dashboard?search=&branch=&cgpa_min=&cgpa_max=&skills=&placement_status=&sort_by=&page=

Query Params:
  - search: str (searches name + roll_no, case-insensitive)
  - branch: str (filter by branch code)
  - cgpa_min: decimal (min CGPA)
  - cgpa_max: decimal (max CGPA)
  - skills: str (comma-separated, matches any)
  - placement_status: str (not_placed | in_process | placed)
  - sort_by: str (name | -name | roll_no | -roll_no | cgpa | -cgpa | created_at | -created_at)
  - page: int (default 1, 20 per page)
```

### Placement Status Update
```
POST /tpo/student/<id>
Body (form):
  - placement_status: str
  - company_name: str (if placed)
  - package: decimal (if placed)
```

### CSV Export
```
GET /tpo/export-csv?<same filter params as dashboard>
Response: text/csv attachment
Columns: Roll No, Name, Email, Branch, CGPA, Skills, Status, Company, Package, Has Resume
```

### Bulk Resume Download
```
GET /tpo/bulk-download?<same filter params as dashboard>
Response: application/zip attachment
Contents: {roll_no}_{name}.pdf for each matching student with resume
```

### Drive Creation
```
POST /tpo/drives/create
Body (form):
  - company_name: str (required)
  - role: str (required)
  - package: decimal (required)
  - description: str (optional)
  - min_cgpa: decimal (optional, default 0)
  - allowed_branches: list[str] (multi-select)
  - no_active_backlogs: str (any | no_active | no_history)
  - deadline: date (YYYY-MM-DD, optional)
```

### Application Status Update
```
POST /tpo/drives/application/<app_id>/status
Body (form):
  - status: str (shortlisted | rejected | offered)
```

---

## 6. Analytics Data Returned to Template

```python
# Context variable: analytics
{
    'total_students': int,
    'cgpa_distribution': {
        '9.0-10.0': int,
        '8.0-8.99': int,
        '7.0-7.99': int,
        '6.0-6.99': int,
        'Below 6.0': int,
    },
    'branch_distribution': {
        'CSE': int,
        'ECE': int,
        ...
    },
    'placement_stats': {
        'placed': int,
        'in_process': int,
        'not_placed': int,
        'placement_rate': float,  # percentage
    },
    'top_skills': {
        'Python': int,
        'Java': int,
        ...  # top 10
    }
}
```
