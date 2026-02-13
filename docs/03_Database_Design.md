# Database Design Document
## Resume Bank Management System — MySQL Schema

| Field | Value |
|-------|-------|
| **Database Engine** | MySQL 8.x |
| **ORM** | Django ORM |
| **Character Set** | utf8mb4 |
| **Collation** | utf8mb4_unicode_ci |
| **Date** | 2026-02-13 |

---

## 1. Entity-Relationship Diagram

```
┌──────────────────┐       1:1        ┌──────────────────────────┐
│      User        │─────────────────▶│       Student             │
│                  │                  │                          │
│  id (PK)         │                  │  id (PK)                 │
│  email (UNIQUE)  │                  │  user_id (FK → User)     │
│  password        │                  │  name                    │
│  role            │                  │  roll_no (UNIQUE)        │
│  is_active       │                  │  email                   │
│  date_joined     │                  │  branch                  │
│  last_login      │                  │  cgpa                    │
└──────────────────┘                  │  skills                  │
                                      │  resume (FileField)      │
                                      │  placement_status        │
                                      │  company_name            │
                                      │  package                 │
                                      │  created_at              │
                                      │  updated_at              │
                                      └──────────┬───────────────┘
                                                 │
                                                 │ 1:N
                                                 ▼
┌──────────────────────────┐          ┌──────────────────────────┐
│         Drive            │          │      Application         │
│                          │          │                          │
│  id (PK)                 │          │  id (PK)                 │
│  company_name            │ 1:N      │  drive_id (FK → Drive)   │
│  role                    │─────────▶│  student_id (FK→Student) │
│  package                 │          │  applied_at              │
│  description             │          │  status                  │
│  min_cgpa                │          └──────────────────────────┘
│  allowed_branches        │
│  backlogs_criteria       │
│  deadline                │
│  status                  │
│  created_at              │
└──────────────────────────┘
```

---

## 2. Table Definitions

### 2.1 `auth_user` (Django Built-in, Extended)

Django's `AbstractUser` provides this table automatically. We add a `role` field.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `INT` | PK, AUTO_INCREMENT | |
| `username` | `VARCHAR(150)` | UNIQUE, NOT NULL | Set to email |
| `email` | `VARCHAR(254)` | UNIQUE, NOT NULL | Primary identifier |
| `password` | `VARCHAR(128)` | NOT NULL | Django hashed password |
| `role` | `VARCHAR(10)` | NOT NULL, DEFAULT 'student' | 'student' or 'admin' |
| `first_name` | `VARCHAR(150)` | | Optional |
| `last_name` | `VARCHAR(150)` | | Optional |
| `is_staff` | `BOOLEAN` | DEFAULT FALSE | For Django admin access |
| `is_active` | `BOOLEAN` | DEFAULT TRUE | Account enabled |
| `is_superuser` | `BOOLEAN` | DEFAULT FALSE | |
| `date_joined` | `DATETIME` | NOT NULL | Auto-set |
| `last_login` | `DATETIME` | NULLABLE | Auto-updated |

**Indexes**: `email` (UNIQUE), `role`

---

### 2.2 `students_student`

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `INT` | PK, AUTO_INCREMENT | |
| `user_id` | `INT` | FK → `auth_user.id`, UNIQUE, ON DELETE CASCADE | One-to-One |
| `name` | `VARCHAR(100)` | NOT NULL | |
| `roll_no` | `VARCHAR(20)` | UNIQUE, NOT NULL | e.g., CSE2021001 |
| `email` | `VARCHAR(254)` | NOT NULL | Denormalized from User |
| `branch` | `VARCHAR(10)` | NOT NULL | See branch choices below |
| `cgpa` | `DECIMAL(4,2)` | NOT NULL, CHECK (0.00 ≤ cgpa ≤ 10.00) | |
| `skills` | `TEXT` | NOT NULL | Comma-separated or JSON |
| `resume` | `VARCHAR(255)` | NULLABLE | File path in `media/resumes/` |
| `placement_status` | `VARCHAR(15)` | NOT NULL, DEFAULT 'not_placed' | Enum-style |
| `company_name` | `VARCHAR(100)` | NULLABLE | Required if placed |
| `package` | `DECIMAL(6,2)` | NULLABLE | LPA, required if placed |
| `created_at` | `DATETIME` | NOT NULL, auto_now_add | |
| `updated_at` | `DATETIME` | NOT NULL, auto_now | |

**Indexes**: `user_id` (UNIQUE), `roll_no` (UNIQUE), `email`, `branch`, `cgpa`, `placement_status`

**Branch Choices**:
```
CSE, ECE, EEE, ME, CE, IT, AI&DS
```

**Placement Status Choices**:
```
not_placed, in_process, placed
```

---

### 2.3 `tpo_drive`

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `INT` | PK, AUTO_INCREMENT | |
| `company_name` | `VARCHAR(100)` | NOT NULL | |
| `role` | `VARCHAR(100)` | NOT NULL | Job role title |
| `package` | `DECIMAL(6,2)` | NOT NULL | LPA |
| `description` | `TEXT` | NULLABLE | Job description |
| `min_cgpa` | `DECIMAL(4,2)` | DEFAULT 0.00 | Eligibility criterion |
| `allowed_branches` | `VARCHAR(200)` | NULLABLE | Comma-separated branch codes |
| `backlogs_criteria` | `VARCHAR(20)` | DEFAULT 'any' | 'any', 'no_active', 'no_history' |
| `deadline` | `DATE` | NULLABLE | Application deadline |
| `status` | `VARCHAR(15)` | NOT NULL, DEFAULT 'active' | 'active', 'closed', 'completed' |
| `created_at` | `DATETIME` | NOT NULL, auto_now_add | |

**Indexes**: `status`, `created_at`

---

### 2.4 `tpo_application`

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `INT` | PK, AUTO_INCREMENT | |
| `drive_id` | `INT` | FK → `tpo_drive.id`, ON DELETE CASCADE | |
| `student_id` | `INT` | FK → `students_student.id`, ON DELETE CASCADE | |
| `applied_at` | `DATETIME` | NOT NULL, auto_now_add | |
| `status` | `VARCHAR(15)` | NOT NULL, DEFAULT 'applied' | See status choices |

**Indexes**: (`drive_id`, `student_id`) — UNIQUE composite index  
**Status Choices**: `applied`, `shortlisted`, `rejected`, `offered`

---

## 3. Django Model Definitions (Reference)

```python
# accounts/models.py
class User(AbstractUser):
    ROLE_CHOICES = [('student', 'Student'), ('admin', 'Admin')]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')

# students/models.py
class Student(models.Model):
    BRANCH_CHOICES = [
        ('CSE', 'Computer Science Engineering'),
        ('ECE', 'Electronics & Communication Engineering'),
        ('EEE', 'Electrical & Electronics Engineering'),
        ('ME', 'Mechanical Engineering'),
        ('CE', 'Civil Engineering'),
        ('IT', 'Information Technology'),
        ('AI&DS', 'Artificial Intelligence & Data Science'),
    ]
    PLACEMENT_STATUS_CHOICES = [
        ('not_placed', 'Not Placed'),
        ('in_process', 'In Process'),
        ('placed', 'Placed'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    roll_no = models.CharField(max_length=20, unique=True)
    email = models.EmailField()
    branch = models.CharField(max_length=10, choices=BRANCH_CHOICES)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2)
    skills = models.TextField(help_text='Comma-separated')
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    placement_status = models.CharField(max_length=15, choices=PLACEMENT_STATUS_CHOICES, default='not_placed')
    company_name = models.CharField(max_length=100, blank=True, null=True)
    package = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# tpo/models.py
class Drive(models.Model):
    company_name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    package = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    min_cgpa = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    allowed_branches = models.CharField(max_length=200, blank=True)
    backlogs_criteria = models.CharField(max_length=20, default='any')
    deadline = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=15, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

class Application(models.Model):
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
        ('offered', 'Offered'),
    ]
    drive = models.ForeignKey(Drive, on_delete=models.CASCADE, related_name='applications')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='applications')
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='applied')

    class Meta:
        unique_together = ('drive', 'student')
```

---

## 4. MongoDB → MySQL Migration Notes

| MongoDB Concept | MySQL / Django Equivalent |
|----------------|---------------------------|
| `ObjectId` | Auto-increment `INT` primary key |
| `db.collection.find_one()` | `Model.objects.get()` / `.filter().first()` |
| `db.collection.find()` | `Model.objects.filter()` |
| `db.collection.insert_one()` | `Model.objects.create()` or `model.save()` |
| `db.collection.update_one()` | `Model.objects.filter().update()` or `model.save()` |
| `db.collection.count_documents()` | `Model.objects.filter().count()` |
| `$regex` search | `__icontains` / `Q` objects |
| `$gte` / `$lte` | `__gte` / `__lte` |
| `$in` | `__in` |
| `$or` conditions | `Q(cond1) | Q(cond2)` |
| Aggregation `$group` | `.values().annotate(Count())` |
| Aggregation `$unwind` | Custom query or Python-level processing |
| `.sort()` | `.order_by()` |
| `.skip().limit()` | Django Paginator or `[offset:offset+limit]` |
| `$lookup` (join) | `select_related()` / `prefetch_related()` |

---

## 5. Indexes & Performance

| Table | Index | Type | Purpose |
|-------|-------|------|---------|
| `auth_user` | `email` | UNIQUE | Login lookup |
| `students_student` | `user_id` | UNIQUE | OneToOne FK |
| `students_student` | `roll_no` | UNIQUE | Search |
| `students_student` | `branch` | BTREE | Filter |
| `students_student` | `cgpa` | BTREE | Range filter |
| `students_student` | `placement_status` | BTREE | Filter |
| `students_student` | `name` | BTREE | Search/sort |
| `tpo_application` | `(drive_id, student_id)` | UNIQUE COMPOSITE | Prevent duplicates |
| `tpo_drive` | `status` | BTREE | Active drives filter |
