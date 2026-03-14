# TNPHelper — Project Architecture & Documentation

TNPHelper is a **Resume Bank Management System** designed for a university Training & Placement Cell (TPO). It is built using the **Django** web framework (Python) with a **MySQL** database backend. The application features a split portal system: one for **Students** and one for **TPO Administrators**.

This document explains the technical architecture, data models, and features of the project in detail.

---

## 1. Project Structure

The project follows a standard Django multi-app architecture.

```text
TNPHelper/
├── manage.py               # Django management script
├── resume_bank/            # Main project configuration folder
│   ├── settings.py         # Global settings (Database, Apps, Auth)
│   ├── urls.py             # Root URL routing
│   └── wsgi.py/asgi.py     # Web server entry points
├── accounts/               # Custom Authentication App
├── core/                   # Shared views (Landing page, Error pages)
├── students/               # Student Portal App
├── tpo/                    # TPO Admin Portal App
├── static/                 # CSS (style.css), JS, Images
├── templates/              # HTML Templates (Bootstrap 5 + Custom CSS)
└── media/                  # Uploaded files (Student Resumes in PDF format)
```

---

## 2. Core Applications

The system is divided into four main Django apps to keep concerns separated.

### A. `accounts` (Authentication & Access Control)
Handles custom user login, registration, and role management.
- **Custom User Model**: Extends Django's `AbstractUser` to add a `role` field.
  - `role='student'`: Standard student accounts.
  - `role='admin'`: TPO administrative accounts.
- **Views**: Separated logins — `student_login`, `tpo_login`, and `student_register`.
- **Decorators**: Custom `@student_required` and `@admin_required` decorators ensure secure, role-based access to views across other apps.

### B. `students` (Student Portal)
Handles everything related to a student's profile and placement activities.
- **Dashboard**: Shows profile completion percentage, CGPA, and quick actions.
- **Profile**: Allows students to update their personal info, branch, CGPA, and comma-separated skills.
- **Resume Management**: File upload handler strictly for `.pdf` files. Resumes are saved to the `/media/resumes/` folder using the student's roll number to prevent file collisions.
- **Placement Drives**:
  - `drives_list` view: Students can browse `active` placement drives.
  - `apply_drive` view: One-click apply system. Requires the student to have uploaded a resume first.
  - `my_applications` view: Shows the real-time status of all historically applied drives (Shortlisted, Offered, Rejected, etc.).

### C. `tpo` (Administrator Portal)
Handles student tracking, analytics, data export, and placement drive management.
- **Dashboard**: A directory of all registered students with search, sorting, and pagination (20 students/page).
- **Drive Management**: Admins can create new "Drives", setting parameters like company name, role, package (LPA), minimum CGPA, allowed branches, and backlog policies.
- **Applicant Tracking**: Placed within the drive management, admins view applied students and update their individual application statuses (`Shortlisted`, `Rejected`, or `Offered`).
- **Analytics Dashboard**: Generates comprehensive statistics:
  - CGPA distribution across the college.
  - Top 10 most common skills listed by students.
  - Placement rates (overall and broken down by branch).
- **Data Export**:
  - `export_csv`: Downloads a CSV of student data for reporting.
  - `bulk_download_resumes`: Downloads a ZIP folder containing the resumes of filtered students.

### D. `core`
A lightweight app responsible for serving the public `home.html` landing page and custom error pages (404, 500).

---

## 3. Database Schema (Models)

The database schema utilizes relational mapping (MySQL) to link users, students, and applications.

### 1. `accounts.User`
- Extends Django user.
- Fields: `username`, `email`, `password`, **`role`** (`student` or `admin`).

### 2. `students.Student`
- One-to-One relationship with `accounts.User`.
- Fields: `name`, `roll_no` (Unique), `email`, `branch`, `cgpa`, `skills`, `resume` (FileField).
- Placement fields: `placement_status` (Not Placed, In Process, Placed), `company_name`, `package`.

### 3. `tpo.Drive`
- Represents a company coming for recruitment.
- Fields: `company_name`, `role`, `package`, `description`, `deadline`.
- Eligibility criteria: `min_cgpa`, `allowed_branches`, `backlogs_criteria`.
- Status: `status` (Active, Closed, Completed).

### 4. `tpo.Application`
- The junction/through table representing a student applying to a drive.
- Foreign Keys: `student` (links to `Student`), `drive` (links to `Drive`).
- Constraint: `unique_together = ('drive', 'student')` to prevent duplicate applications.
- Fields: `applied_at`, **`status`** (Applied, Shortlisted, Rejected, Offered).

---

## 4. UI/UX Design System

The frontend is built using **Bootstrap 5.3** combined with a robust custom CSS design system (`style.css`).

- **Aesthetic**: Teal & Slate color palette. Uses modern principles like *glassmorphism* (blur-backed glass panels) and soft shadows (`box-shadow: 0 4px 14px rgba(13, 148, 136, .35)`).
- **Layout**: Uses a sidebar navigation structure (`dashboard_base.html`) for authenticated users, which dynamically hides/shows links based on the user's role (`is_admin` vs `is_student`).
- **Interactivity**: Custom JavaScript handles mobile sidebar toggling, auto-dismissing flash messages (alerts), and protecting against double form submissions (showing a "Processing..." spinner on buttons).
- **Dynamic Status Badges**: Uses Django template logic to dynamically apply CSS classes (e.g., `.status-shortlisted` gives a blue badge, `.status-offered` gives a green badge) based on the database state.

---

## 5. Key Workflows

### Student Registration & Setup Flow
1. Student goes to `/auth/student/register`.
2. Form creates an `accounts.User` (role=student) and a linked `students.Student` profile simultaneously using `transaction.atomic()` to prevent orphaned records if one fails.
3. Student logs in and lands on dashboard. The dashboard calculates a **Profile Completion %** and prompts them to upload a resume.

### Drive Application Flow
1. TPO Admin creates an Active drive in the TPO portal.
2. Student sees it in the "Browse Drives" section.
3. Student clicks "Apply". View checks `if student.resume exists`. If true, an `Application` record is created.
4. TPO Admin goes to the drive's applicants page, reviews resumes, and clicks "Shortlist", "Reject", or "Offer" buttons.
5. The student checks their "My Applications" page and sees the updated color-coded status badge.
