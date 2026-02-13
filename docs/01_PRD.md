# Product Requirements Document (PRD)
## Resume Bank Management System — Training & Placement Cell

| Field | Value |
|-------|-------|
| **Product Name** | Resume Bank Management System (TNP Portal) |
| **Version** | 1.0 |
| **Date** | 2026-02-13 |
| **Status** | Current (Flask+MongoDB) → Planned Migration (Django+MySQL) |

---

## 1. Executive Summary

The Resume Bank Management System is a web application designed for College **Training & Placement Officers (TPO)** to manage student resumes, track placement data, and facilitate campus recruitment drives. It serves two primary user groups — **students** who register, upload resumes, and apply to drives, and **TPO administrators** who manage the student directory, run analytics, and coordinate placement drives.

---

## 2. Problem Statement

College placement cells currently rely on manual spreadsheets, emails, and paper-based systems to:
- Collect and store student resumes
- Track placement status across hundreds of students
- Coordinate with companies and manage recruitment drives
- Generate reports and analytics on placement data

This leads to data silos, version-control issues, and delayed decision-making.

---

## 3. Product Goals

| # | Goal | Success Metric |
|---|------|----------------|
| G1 | Centralize student resume & profile data | 100% of registered students have digital profiles |
| G2 | Enable students to self-manage profiles & resumes | < 2 min to upload/update a resume |
| G3 | Provide TPO with powerful search, filter & export tools | TPO can locate any student record in < 10s |
| G4 | Deliver actionable placement analytics | Dashboard loads with live charts in < 3s |
| G5 | Streamline placement drive lifecycle | End-to-end drive creation → applicant tracking |

---

## 4. User Personas

### 4.1 Student
- **Who**: College students (UG/PG) seeking campus placements
- **Needs**: Register, maintain profile, upload resume, view & apply to active drives
- **Pain Points**: Repeatedly sending updated resumes via email, no visibility into drive status

### 4.2 TPO Administrator
- **Who**: Training & Placement Officer or staff member
- **Needs**: View all students, filter/sort, update placement status, download resumes in bulk, view analytics, manage drives
- **Pain Points**: Manual data aggregation, no single source of truth

---

## 5. Functional Requirements

### 5.1 Module 1 — Student Portal

| ID | Feature | Description | Priority |
|----|---------|-------------|----------|
| F-S01 | Registration | Register with email, password, name, roll number, branch, CGPA, skills | P0 |
| F-S02 | Login / Logout | Email + password authentication with session management | P0 |
| F-S03 | Dashboard | View profile summary, resume status, placement status | P0 |
| F-S04 | Profile Management | Edit name, branch, CGPA, skills, placement status, company, package | P0 |
| F-S05 | Resume Upload | Upload PDF resume (max 10 MB), replace existing | P0 |
| F-S06 | Resume Download | Download own uploaded resume | P1 |
| F-S07 | View Placement Drives | List active placement drives with eligibility criteria | P1 |
| F-S08 | Apply to Drives | One-click apply to eligible drives (requires uploaded resume) | P1 |

### 5.2 Module 2 — TPO (Admin) Portal

| ID | Feature | Description | Priority |
|----|---------|-------------|----------|
| F-T01 | Admin Login / Logout | Email + password auth restricted to admin role | P0 |
| F-T02 | Student Directory | Paginated list of all students (20/page) | P0 |
| F-T03 | Advanced Filtering | Filter by name, roll no, branch, CGPA range, skills, placement status | P0 |
| F-T04 | Sorting | Sort by name, roll no, CGPA, date (asc/desc) | P0 |
| F-T05 | Student Detail View | View complete student profile | P0 |
| F-T06 | Placement Status Updates | Update student's placement status, company, package | P0 |
| F-T07 | Individual Resume Download | Download a specific student's resume | P1 |
| F-T08 | CSV Export | Export filtered student data as CSV | P1 |
| F-T09 | Bulk Resume Download | Download all filtered resumes as ZIP | P1 |
| F-T10 | Analytics Dashboard | Charts — CGPA distribution, branch stats, placement rate, top skills | P0 |
| F-T11 | Drive Management | Create drives with company, role, package, criteria, deadline | P1 |
| F-T12 | View Drive Applicants | List students who applied; shortlist/reject/offer actions | P1 |

---

## 6. Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NF01 | **Performance** — Page load time | < 2 seconds on 3G |
| NF02 | **Security** — Password storage | Bcrypt hashing (≥ 12 salt rounds) |
| NF03 | **Security** — CSRF Protection | Token-based via Django middleware |
| NF04 | **Security** — File Uploads | Extension validation (PDF only), max 10 MB |
| NF05 | **Security** — Session Management | HTTP-only, SameSite cookies |
| NF06 | **Security** — Role-Based Access Control | Decorators/mixins for admin vs student |
| NF07 | **Scalability** | Handle ≥ 5,000 student records |
| NF08 | **Responsiveness** | Mobile-first, Bootstrap 5 grid |
| NF09 | **Browser Support** | Chrome, Firefox, Edge (latest 2 versions) |

---

## 7. Data Entities (Summary)

| Entity | Key Fields |
|--------|------------|
| **User** | email, password_hash, role (student/admin), timestamps |
| **Student** | name, roll_no, email, branch, CGPA, skills[], resume_path, placement_status, company_name, package, timestamps |
| **Drive** | company_name, role, package, description, criteria (min_cgpa, branches, backlogs), deadline, status, timestamps |
| **Application** | drive_id → Drive, student_id → Student, applied_at, status (applied/shortlisted/rejected/offered) |

---

## 8. Branch Options

| Code | Full Name |
|------|-----------|
| CSE | Computer Science Engineering |
| ECE | Electronics & Communication Engineering |
| EEE | Electrical & Electronics Engineering |
| ME | Mechanical Engineering |
| CE | Civil Engineering |
| IT | Information Technology |
| AI&DS | Artificial Intelligence & Data Science |

---

## 9. UI Pages Summary

| # | Page | Portal | Description |
|---|------|--------|-------------|
| 1 | Landing Page | Public | Hero section, features, portal links |
| 2 | Student Login | Student | Email/password form |
| 3 | Student Register | Student | Multi-field registration form |
| 4 | Student Dashboard | Student | Profile card, resume status, quick stats |
| 5 | Edit Profile | Student | Update personal & placement info |
| 6 | Upload Resume | Student | PDF upload with drag-drop |
| 7 | Placement Drives | Student | List active drives, apply button |
| 8 | TPO Login | Admin | Email/password form |
| 9 | TPO Dashboard | Admin | Student directory + filters sidebar |
| 10 | Student Detail | Admin | Full student profile + status update form |
| 11 | Analytics | Admin | Chart.js charts (bar, pie, doughnut) |
| 12 | Drives List | Admin | All drives with status |
| 13 | Create Drive | Admin | Form to create placement drive |
| 14 | Drive Applicants | Admin | Applicants table + shortlist/reject actions |

---

## 10. Out of Scope (v1)

- Email/SMS notifications
- Student-to-student messaging
- Multiple file uploads (only single PDF)
- Third-party SSO (Google/Microsoft login)
- Mobile native app
- Real-time collaboration

---

## 11. Release Plan

| Phase | Scope | Timeline |
|-------|-------|----------|
| Phase 1 | Core Auth + Student Portal (F-S01 to F-S06) | Week 1-2 |
| Phase 2 | TPO Dashboard + Analytics (F-T01 to F-T10) | Week 2-3 |
| Phase 3 | Placement Drives (F-T11, F-T12, F-S07, F-S08) | Week 3-4 |
| Phase 4 | Polish, Testing, Deployment | Week 4-5 |
