# TNPHelper — DevOps & Deployment Guide

> **Audience**: DevOps / System Administrator
> **Stack**: Django 4.2 · MySQL (Amazon RDS or XAMPP) · Gunicorn · Nginx · AWS EC2

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Repository Structure](#2-repository-structure)
3. [Technology Stack](#3-technology-stack)
4. [Database Information](#4-database-information)
5. [Environment Variables & Secrets](#5-environment-variables--secrets)
6. [AWS EC2 Deployment — Step-by-Step](#6-aws-ec2-deployment--step-by-step)
7. [Nginx Configuration](#7-nginx-configuration)
8. [Systemd Service (Gunicorn)](#8-systemd-service-gunicorn)
9. [Static & Media Files](#9-static--media-files)
10. [Amazon RDS Setup](#10-amazon-rds-setup)
11. [AWS S3 Private Resume Storage](#11-aws-s3-private-resume-storage)
12. [Security Checklist for Production](#12-security-checklist-for-production)
13. [Health Checks & Monitoring](#13-health-checks--monitoring)
14. [Rollback & Redeployment](#14-rollback--redeployment)
15. [Port & Firewall Reference](#15-port--firewall-reference)

---

## 1. Project Overview

**TNPHelper** is a Django web application for a university Training & Placement Cell (TPO).
It provides:

- A **Student Portal** — for student registration, profile management, resume upload, and drive applications.
- A **TPO Admin Portal** — for student directory, analytics, data export (CSV/ZIP), and placement drive management.

| Item | Value |
|------|-------|
| **Framework** | Django 4.2 LTS |
| **Language** | Python 3.10+ |
| **Database** | MySQL 8.x (Amazon RDS recommended) |
| **WSGI Server** | Gunicorn |
| **Reverse Proxy** | Nginx |
| **Static Files** | WhiteNoise |
| **Media Files** | AWS S3 (private bucket + pre-signed URLs) · Local disk (`media/resumes/`) fallback |

---

## 2. Repository Structure

```
TNPHelper/                          <- Project root
|
+-- manage.py                       <- Django management CLI entry point
+-- requirements.txt                <- All Python dependencies (pip install -r)
+-- setup.py                        <- Sample data seeder (dev/test use only)
+-- .gitignore                      <- Excluded files (env, media, __pycache__)
|
+-- resume_bank/                    <- Django PROJECT configuration package
|   +-- __init__.py
|   +-- settings.py                 <- Main settings (DB, apps, auth, static/media)
|   +-- urls.py                     <- Root URL router (includes all app URLs)
|   +-- wsgi.py                     <- WSGI entry point -> used by Gunicorn
|
+-- accounts/                       <- APP: Authentication & User management
|   +-- models.py                   <- Custom User model (AbstractUser + role field)
|   +-- views.py                    <- Login, register, logout views (student & TPO)
|   +-- forms.py                    <- Registration, login, TPO login forms
|   +-- decorators.py               <- @admin_required, @student_required guards
|   +-- admin.py                    <- Django admin registration
|   +-- urls.py                     <- URL patterns under /auth/
|   +-- migrations/                 <- DB migrations for accounts app
|
+-- students/                       <- APP: Student Portal
|   +-- models.py                   <- Student model (profile, resume FileField, CGPA)
|   +-- views.py                    <- Dashboard, profile edit, resume upload/download
|   +-- forms.py                    <- StudentProfileForm, ResumeUploadForm (PDF)
|   +-- admin.py                    <- Django admin for Student model
|   +-- urls.py                     <- URL patterns under /student/
|   +-- migrations/                 <- DB migrations for students app
|
+-- tpo/                            <- APP: TPO Admin Portal
|   +-- models.py                   <- Drive model, Application model (junction table)
|   +-- views.py                    <- Student directory, analytics, CSV/ZIP export
|   +-- forms.py                    <- Filter, status update, drive creation forms
|   +-- utils.py                    <- apply_student_filters() — shared filter utility
|   +-- admin.py                    <- Django admin for Drive, Application
|   +-- urls.py                     <- URL patterns under /tpo/
|   +-- migrations/                 <- DB migrations for tpo app
|
+-- core/                           <- APP: Public Pages & Error Handlers
|   +-- views.py                    <- home() landing page, custom_404, custom_500
|   +-- urls.py                     <- URL pattern for /
|   +-- apps.py                     <- App config
|
+-- templates/                      <- Global HTML templates (Django Template Language)
|   +-- base.html                   <- Root layout (head, Bootstrap CDN, meta tags)
|   +-- dashboard_base.html         <- Sidebar layout for authenticated pages
|   +-- home.html                   <- Public landing page
|   +-- 404.html                    <- Custom 404 page
|   +-- 500.html                    <- Custom 500 page
|   +-- accounts/                   <- Auth templates
|   |   +-- student_login.html
|   |   +-- student_register.html
|   |   +-- tpo_login.html
|   +-- students/                   <- Student portal templates
|   |   +-- dashboard.html
|   |   +-- profile.html
|   |   +-- upload_resume.html
|   |   +-- drives.html
|   |   +-- my_applications.html
|   +-- tpo/                        <- TPO admin portal templates
|       +-- dashboard.html
|       +-- student_detail.html
|       +-- analytics.html
|       +-- drives/
|           +-- list.html
|           +-- create.html
|           +-- applicants.html
|
+-- static/                         <- Static assets (committed to repo)
|   +-- css/
|   |   +-- style.css               <- Custom CSS design system
|   +-- favicon.svg                 <- Site favicon
|
+-- media/                          <- Uploaded files (NOT committed — gitignored)
|   +-- resumes/                    <- Student resume PDFs ({roll_no}_resume.pdf)
|
+-- docs/                           <- Project documentation (gitignored)
|   +-- 01_PRD.md
|   +-- 02_System_Design_Document.md
|   +-- 03_Database_Design.md
|   +-- 04_API_Specification.md
|   +-- 05_Django_Migration_Guide.md
|   +-- 06_UI_Design_Document.md
|
+-- README.md                       <- Developer-facing documentation
+-- DEVOPS.md                       <- This file — deployment & ops guide
+-- QUICK_START.md                  <- 5-minute local setup guide
+-- project_architecture.md         <- Architecture overview diagram
```

### Key Files for Deployment

| File | Role |
|------|------|
| `resume_bank/wsgi.py` | Gunicorn WSGI entry point |
| `resume_bank/settings.py` | All configuration — update for production |
| `requirements.txt` | Install with `pip install -r requirements.txt` |
| `manage.py` | Run migrations, collectstatic, createsuperuser |

---

## 3. Technology Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| **Language** | Python 3.10+ | Use 3.10 or 3.11 on EC2 |
| **Framework** | Django 4.2.16 (LTS) | Supported until April 2026 |
| **Database** | MySQL 8.x | Amazon RDS (prod) / XAMPP (dev) |
| **DB Connector** | mysqlclient 2.2.4 | Requires `libmysqlclient-dev` on Linux |
| **WSGI Server** | Gunicorn 23.0 | Binds to Unix socket; Nginx proxies to it |
| **Reverse Proxy** | Nginx | Handles HTTPS, static files, rate limiting |
| **Static Files** | WhiteNoise 6.8 | Compresses and caches static assets |
| **Env Management** | python-decouple 3.8 | Reads from `.env` file |
| **Frontend** | Bootstrap 5.3 (CDN) + Chart.js (CDN) | No build step needed |
| **File Storage** | Local disk `media/` | S3 optional (boto3 + django-storages) |

---

## 4. Database Information

### Database Name

```
tnp_db
```

> **This is the exact database name** configured in `resume_bank/settings.py`.
> When you import the XAMPP database dump into RDS or a new MySQL instance, create the database with this name.

### Database Connection Details (Local XAMPP Default)

| Setting | Value |
|---------|-------|
| **Database Name** | `tnp_db` |
| **Engine** | MySQL (InnoDB, utf8mb4) |
| **User** | `root` |
| **Password** | *(empty by default in XAMPP)* |
| **Host** | `localhost` |
| **Port** | `3306` |
| **Charset** | `utf8mb4` |
| **Collation** | `utf8mb4_general_ci` |

### Tables Created by Django Migrations

| Table | Django App | Description |
|-------|-----------|-------------|
| `accounts_user` | accounts | Custom User (AbstractUser + role field) |
| `auth_permission` | django.contrib.auth | Django built-in |
| `auth_group` | django.contrib.auth | Django built-in |
| `auth_group_permissions` | django.contrib.auth | Django built-in |
| `auth_user_groups` | django.contrib.auth | Django built-in |
| `auth_user_user_permissions` | django.contrib.auth | Django built-in |
| `django_admin_log` | django.contrib.admin | Admin action log |
| `django_content_type` | django.contrib.contenttypes | Content types |
| `django_migrations` | django.db.migrations | Migration tracker |
| `django_session` | django.contrib.sessions | Session storage |
| `students_student` | students | Student profiles + resume path |
| `tpo_drive` | tpo | Placement drives |
| `tpo_application` | tpo | Student drive applications (junction) |

### Import XAMPP Database Dump

When the SQL dump file (`tnp_db.sql`) is included in the repository:

```bash
# Create the database first
mysql -u <user> -p -h <host> -e "CREATE DATABASE tnp_db CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;"

# Import the dump
mysql -u <user> -p -h <host> tnp_db < tnp_db.sql
```

---

## 5. Environment Variables & Secrets

Create a `.env` file in the project root (same directory as `manage.py`).
**Never commit this file to Git** — it is listed in `.gitignore`.

```ini
# .env — TNPHelper Production Configuration

# Django Core
SECRET_KEY=your-very-long-random-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-ec2-ip,your-domain.com

# Database (Amazon RDS or MySQL)
DB_NAME=tnp_db
DB_USER=tnp_user
DB_PASSWORD=your-strong-db-password
DB_HOST=your-rds-endpoint.rds.amazonaws.com
DB_PORT=3306

# AWS S3 — Private Resume Storage (leave keys blank if using EC2 IAM Role)
AWS_STORAGE_BUCKET_NAME=tnphelper-resumes-prod
AWS_S3_REGION_NAME=ap-south-1
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_S3_PRESIGNED_URL_EXPIRY=300
```

> **Generate a secret key:**
> ```bash
> python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
> ```

### Update `settings.py` to Use `.env`

Add `python-decouple` reads at the top of `resume_bank/settings.py`:

```python
from decouple import config

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost').split(',')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME', default='tnp_db'),
        'USER': config('DB_USER', default='root'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
```

Also add `STATIC_ROOT` for `collectstatic`:

```python
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

---

## 6. AWS EC2 Deployment — Step-by-Step

### 6.1 Recommended EC2 Configuration

| Setting | Recommendation |
|---------|---------------|
| **AMI** | Ubuntu 22.04 LTS or Amazon Linux 2023 |
| **Instance Type** | `t3.micro` (free tier) / `t3.small` (production) |
| **Storage** | 20 GB gp3 EBS (increase if storing many resumes) |
| **Security Group** | Allow: SSH (22), HTTP (80), HTTPS (443) |

### 6.2 Server Setup (Ubuntu 22.04)

```bash
# 1. Update the system
sudo apt update && sudo apt upgrade -y

# 2. Install Python 3.10, pip, venv
sudo apt install -y python3.10 python3.10-venv python3-pip

# 3. Install MySQL client library (required to compile mysqlclient)
sudo apt install -y libmysqlclient-dev default-libmysqlclient-dev pkg-config

# 4. Install Nginx
sudo apt install -y nginx
```

### 6.3 Application Setup

```bash
# 1. Create app directory
sudo mkdir -p /var/www/tnphelper
sudo chown $USER:$USER /var/www/tnphelper
cd /var/www/tnphelper

# 2. Clone the repository
git clone https://github.com/your-org/TNPHelper.git .

# 3. Create Python virtual environment
python3.10 -m venv venv
source venv/bin/activate

# 4. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 5. Create .env file (fill in values from Section 5)
nano .env

# 6. Create media directory for uploaded resumes
mkdir -p media/resumes

# 7. Collect static files
python manage.py collectstatic --noinput

# 8. Run database migrations
python manage.py migrate

# 9. Create Django superuser (TPO admin)
python manage.py createsuperuser
```

### 6.4 Test Gunicorn Manually

```bash
gunicorn resume_bank.wsgi:application --bind 0.0.0.0:8000 --workers 3
# Ctrl+C to stop — Nginx handles this in production via Unix socket
```

---

## 7. Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/tnphelper
```

```nginx
server {
    listen 80;
    server_name YOUR_DOMAIN_OR_IP;

    # Static files served by Nginx directly
    location /static/ {
        alias /var/www/tnphelper/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }

    # Media files (uploaded student resumes)
    # NOTE: When S3 is enabled (AWS_STORAGE_BUCKET_NAME is set), resumes are
    # stored in private S3 and served via pre-signed URLs. This block is only
    # used when running with local disk storage (development / non-S3 fallback).
    location /media/ {
        alias /var/www/tnphelper/media/;
    }

    # Proxy everything else to Gunicorn
    location / {
        proxy_pass http://unix:/run/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 12M;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/tnphelper /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 8. Systemd Service (Gunicorn)

```bash
sudo nano /etc/systemd/system/gunicorn.service
```

```ini
[Unit]
Description=Gunicorn daemon for TNPHelper
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/tnphelper
EnvironmentFile=/var/www/tnphelper/.env
ExecStart=/var/www/tnphelper/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          --access-logfile /var/log/gunicorn/access.log \
          --error-logfile /var/log/gunicorn/error.log \
          resume_bank.wsgi:application
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo mkdir -p /var/log/gunicorn
sudo chown www-data:www-data /var/log/gunicorn
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl start gunicorn
sudo systemctl status gunicorn
```

---

## 9. Static & Media Files

### Static Files

```bash
# Run once after each deployment
python manage.py collectstatic --noinput
# Creates: /var/www/tnphelper/staticfiles/
```

| `settings.py` Key | Value |
|-------------------|-------|
| `STATIC_URL` | `/static/` |
| `STATICFILES_DIRS` | `[BASE_DIR / 'static']` |
| `STATIC_ROOT` | `BASE_DIR / 'staticfiles'` (add this!) |

### Media Files (Student Resume PDFs)

The system supports two storage modes with automatic selection:

1. **Production (AWS S3)**: Activated whenever `AWS_STORAGE_BUCKET_NAME` is set in `.env`.
   - Files are stored in a private S3 bucket (`s3://<bucket>/resumes/<filename>.pdf`).
   - Resumes are served through **time-limited pre-signed URLs** (default 300 seconds / 5 minutes).
   - The user/admin browser downloads directly from S3, saving EC2 bandwidth and Gunicorn memory.
   - TPO Admin bulk downloads (ZIP) stream file bytes directly from S3 into an archive stream without saving files to the EC2 filesystem.
   - See [Section 11](#11-aws-s3-private-resume-storage) for full configuration.

2. **Local Fallback (Development / CI)**: Activated when `AWS_STORAGE_BUCKET_NAME` is omitted.
   - Files are stored on local disk under `media/resumes/`.
   - The `media/` directory is **gitignored**.
   - Resumes are streamed securely via authenticated Django `FileResponse` views.

| Parameter | S3 Mode (Production) | Local Mode (Development) |
|-----------|----------------------|--------------------------|
| Storage Backend | `PrivateS3ResumeStorage` (boto3) | `LocalResumeStorage` (`FileSystemStorage`) |
| Bucket / Directory | `s3://<AWS_STORAGE_BUCKET_NAME>/resumes/` | `BASE_DIR / 'media' / 'resumes/'` |
| Access Control | Authenticated 302 redirect → S3 Pre-signed URL | Authenticated Django `FileResponse` view |
| Max Upload Size | 5 MB (`MAX_RESUME_SIZE` configurable) | 5 MB (`MAX_RESUME_SIZE` configurable) |
| Allowed Types | `.pdf` only | `.pdf` only |

---

## 10. Amazon RDS Setup

### Create RDS Instance

1. AWS Console > RDS > Create database
2. Engine: **MySQL 8.x**, tier: `db.t3.micro`
3. DB identifier: `tnphelper-db`
4. Master username: `tnp_user`, password: (strong)
5. Connectivity: same VPC as EC2; SG allows port 3306 from EC2 SG
6. Initial database name: **`tnp_db`**

### Connect & Import

```bash
# Test connection from EC2
mysql -h YOUR_RDS_ENDPOINT -u tnp_user -p tnp_db

# Option A: Import XAMPP dump
mysql -h YOUR_RDS_ENDPOINT -u tnp_user -p tnp_db < tnp_db.sql

# Option B: Fresh migrations
python manage.py migrate
```

---

## 11. AWS S3 Private Resume Storage

TNPHelper stores student resumes in an **Amazon S3 Private Bucket** for production deployments, backed by secure, time-limited **pre-signed URLs**.

---

### 11.1 Architecture & Security Overview

```
                      +-----------------------------------+
                      |         Student / TPO Admin       |
                      +-----------------+-----------------+
                                        |
       1. Request Resume Download       |   3. HTTP 302 Redirect
          (authenticated request)       |      to Pre-signed S3 URL
                                        v
                            +-----------------------+
                            |   EC2 (Django App)    |
                            +-----------+-----------+
                                        | 2. Generate Pre-signed URL
                                        |    via Boto3 (5 min expiry)
                                        v
                            +-----------------------+
                            |  Amazon S3 (Private)  |
                            +-----------+-----------+
                                        ^
       4. Direct Download               |
          (stream PDF directly from S3) |
          +-----------------------------+
```

#### Why a Private S3 Bucket?
- Resumes contain student Personally Identifiable Information (PII): phone numbers, email addresses, residential addresses, and academic records.
- The S3 bucket is **strictly private** (`Block Public Access` = ON). Public URLs (`https://<bucket>.s3.amazonaws.com/...`) will return `403 Access Denied`.
- Resumes are downloaded only through **authenticated Django views** which generate cryptographic, time-limited pre-signed URLs (default: **5 minutes / 300 seconds**).
- **Zero EC2 Proxying**: The browser downloads the PDF directly from AWS S3. Gunicorn worker threads and EC2 bandwidth are not consumed streaming large binary files.
- **TPO Admin Bulk ZIP**: TPO admins can download applicant resumes as a combined `.zip`. The backend streams object bytes directly from S3 into an archive stream without writing temporary files to EC2 disk.
- **Zero-Downtime Fallback**: If `AWS_STORAGE_BUCKET_NAME` is left blank or unset, Django automatically falls back to local disk (`media/resumes/`) for local development or testing.

---

### 11.2 Step 1: Create and Secure the S3 Bucket

Run these commands using the AWS CLI on your deployment workstation or EC2 instance (ensure AWS CLI has admin privileges):

```bash
# Set your environment variables
export BUCKET_NAME="tnphelper-resumes-prod"
export AWS_REGION="ap-south-1"

# 1. Create the S3 bucket
aws s3api create-bucket \
  --bucket $BUCKET_NAME \
  --region $AWS_REGION \
  --create-bucket-configuration LocationConstraint=$AWS_REGION

# 2. Block ALL public access (MANDATORY FOR SECURITY)
aws s3api put-public-access-block \
  --bucket $BUCKET_NAME \
  --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

# 3. Enable default server-side encryption (SSE-S3 / AES256)
aws s3api put-bucket-encryption \
  --bucket $BUCKET_NAME \
  --server-side-encryption-configuration '{
    "Rules": [
      {
        "ApplyServerSideEncryptionByDefault": {
          "SSEAlgorithm": "AES256"
        }
      }
    ]
  }'

# 4. Enable bucket versioning (Recommended for disaster recovery and audits)
aws s3api put-bucket-versioning \
  --bucket $BUCKET_NAME \
  --versioning-configuration Status=Enabled
```

---

### 11.3 Step 2: Configure IAM Permissions

#### Option A: EC2 IAM Role / Instance Profile (Recommended & Best Practice)
Using an IAM Role eliminates hardcoded AWS access keys on the EC2 instance. The AWS SDK (`boto3`) automatically retrieves and rotates short-lived credentials from the EC2 Instance Metadata Service (IMDS).

1. Create an IAM policy file named `tnphelper-s3-policy.json`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "TNPHelperResumeObjectsAccess",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:HeadObject"
      ],
      "Resource": "arn:aws:s3:::tnphelper-resumes-prod/*"
    },
    {
      "Sid": "TNPHelperResumeBucketList",
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket"
      ],
      "Resource": "arn:aws:s3:::tnphelper-resumes-prod"
    }
  ]
}
```

2. Create the policy in AWS:
```bash
aws iam create-policy \
  --policy-name TNPHelperS3ResumePolicy \
  --policy-document file://tnphelper-s3-policy.json
```

3. Attach the policy to your EC2 instance's IAM Role via AWS Management Console:
   - Go to **EC2 Console** → Select your EC2 Instance → **Actions** → **Security** → **Modify IAM role**.
   - Attach a role that has `TNPHelperS3ResumePolicy` attached.

#### Option B: Dedicated IAM User (Alternative)
If an IAM instance profile cannot be attached to EC2:
1. Create an IAM User (e.g., `tnphelper-s3-app`).
2. Attach the `TNPHelperS3ResumePolicy` directly to the user.
3. Generate Access Keys (**Access Key ID** & **Secret Access Key**) and place them in `/var/www/tnphelper/.env`.

---

### 11.4 Step 3: CORS Configuration (Optional)

If your frontend or administrative dashboard needs to render or preview PDF files directly inside the browser from the domain:

```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "HEAD"],
    "AllowedOrigins": [
      "https://your-domain.com",
      "https://www.your-domain.com"
    ],
    "ExposeHeaders": ["ETag"],
    "MaxAgeSeconds": 3000
  }
]
```

Apply CORS configuration:
```bash
aws s3api put-bucket-cors \
  --bucket tnphelper-resumes-prod \
  --cors-configuration file://cors.json
```

---

### 11.5 Step 4: Environment Variables (`.env`)

Add the following configuration to your production `.env` file at `/var/www/tnphelper/.env`:

```ini
# ── AWS S3 — Private Resume Storage ───────────────────────────────
AWS_STORAGE_BUCKET_NAME=tnphelper-resumes-prod
AWS_S3_REGION_NAME=ap-south-1

# If using an EC2 IAM Role (Option A - Recommended), leave these empty:
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=

# If using an IAM User (Option B), populate your credentials:
# AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
# AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

# Validity duration of pre-signed download URLs in seconds (default: 300 = 5 minutes)
AWS_S3_PRESIGNED_URL_EXPIRY=300

# File Upload Limits
MAX_RESUME_SIZE=5242880
DATA_UPLOAD_MAX_MEMORY_SIZE=10485760
```

> **Security Note:** Set strict permissions on the `.env` file:
> ```bash
> chmod 600 /var/www/tnphelper/.env
> sudo chown www-data:www-data /var/www/tnphelper/.env
> ```

---

### 11.6 Step 5: Migrate Existing Resumes to S3 (One-Time)

If you already have existing student resumes stored on local disk under `media/resumes/`:

```bash
# Sync local resumes to S3 with server-side encryption
aws s3 sync /var/www/tnphelper/media/resumes/ s3://tnphelper-resumes-prod/resumes/ \
  --sse AES256 \
  --no-progress

# Verify file count matches
ls -1 /var/www/tnphelper/media/resumes/*.pdf | wc -l
aws s3 ls s3://tnphelper-resumes-prod/resumes/ | wc -l
```

---

### 11.7 Step 6: Verify and Test Deployment

1. **Verify Django Configuration:**
   ```bash
   cd /var/www/tnphelper
   source venv/bin/activate
   python manage.py check
   ```

2. **Test S3 Connectivity via Django Shell:**
   ```bash
   python manage.py shell -c "
   from students.storage import PrivateS3ResumeStorage
   storage = PrivateS3ResumeStorage()
   print('Connected S3 Bucket:', storage.bucket_name)
   print('Region:', storage.region)
   print('URL Expiry:', storage.expiry, 'seconds')
   "
   ```

3. **Restart Application Services:**
   ```bash
   sudo systemctl restart gunicorn
   sudo systemctl restart nginx
   ```

4. **Functional Checklist:**
   - [ ] Student login → Upload new PDF resume → Verify object is created in S3 under `resumes/`.
   - [ ] Student dashboard → Click "Download Resume" → Verify HTTP 302 redirect to `https://tnphelper-resumes-prod.s3.ap-south-1.amazonaws.com/...` with pre-signed query signature parameters.
   - [ ] TPO Admin portal → Student directory → Click "Download Resume" for a student → Verify valid redirect and file opens correctly.
   - [ ] TPO Admin portal → "Download All Resumes (ZIP)" → Verify `.zip` file is downloaded containing student resumes.

---

### 11.8 Troubleshooting & Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| `AccessDenied (403)` on upload/download | Missing IAM policy permissions or wrong bucket name | Verify that the IAM Role attached to the EC2 instance has `s3:PutObject`, `s3:GetObject`, and `s3:DeleteObject` for `arn:aws:s3:::<bucket>/*`. |
| `SignatureDoesNotMatch` | EC2 server system clock drifted | Boto3 AWS signatures require accurate clock sync. Run `sudo systemctl restart systemd-timesyncd` or verify `chrony` is active. |
| Download link expired (`Request has expired`) | User clicked link after the validity window | Increase `AWS_S3_PRESIGNED_URL_EXPIRY` in `.env` (e.g., `600` for 10 minutes) and restart Gunicorn. |
| Resumes still saving to local disk | `AWS_STORAGE_BUCKET_NAME` not read | Ensure `AWS_STORAGE_BUCKET_NAME` is set in `/var/www/tnphelper/.env` and restart Gunicorn (`sudo systemctl restart gunicorn`). |

---

## 12. Security Checklist for Production

| Item | Action Required |
|------|----------------|
| `DEBUG=False` | Set in `.env` |
| `SECRET_KEY` | Long random string — never commit to Git |
| `ALLOWED_HOSTS` | EC2 IP / domain name only |
| HTTPS | AWS Certificate Manager + ALB, or Certbot (Let's Encrypt) |
| DB password | Strong password, stored only in `.env` |
| `.env` permissions | `chmod 600 .env` |
| `CSRF_TRUSTED_ORIGINS` | `['https://your-domain.com']` |
| `SECURE_SSL_REDIRECT` | `True` when HTTPS is configured |
| File upload validation | Enforced: PDF only, 10 MB max |
| Django admin URL | Consider changing from `/admin/` to something less obvious |
| SQL injection | Already safe — Django ORM uses parameterized queries |

---

## 13. Health Checks & Monitoring

```bash
# Gunicorn
sudo systemctl status gunicorn
sudo journalctl -u gunicorn -f
tail -f /var/log/gunicorn/access.log
tail -f /var/log/gunicorn/error.log

# Nginx
sudo systemctl status nginx
sudo tail -f /var/log/nginx/error.log

# Django deployment check
python manage.py check --deploy
```

---

## 14. Rollback & Redeployment

### Standard Redeployment

```bash
cd /var/www/tnphelper && source venv/bin/activate
git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
```

### Rollback to a Git Tag

```bash
git fetch --tags
git checkout tags/v1.0.0
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
```

---

## 15. Port & Firewall Reference

| Port | Purpose | Inbound Rule |
|------|---------|--------------|
| `22` | SSH | Your admin IP only |
| `80` | HTTP (Nginx) | 0.0.0.0/0 |
| `443` | HTTPS (Nginx + SSL) | 0.0.0.0/0 |
| `8000` | Gunicorn (internal) | NOT exposed — uses Unix socket |
| `3306` | MySQL / RDS | EC2 Security Group only — NEVER 0.0.0.0/0 |

---

## Quick Reference Commands

```bash
sudo systemctl restart gunicorn          # Restart app
sudo journalctl -u gunicorn --since "1 hour ago"  # View recent logs
python manage.py migrate                 # Apply DB migrations
python manage.py collectstatic --noinput # Re-collect static files
python manage.py createsuperuser         # Create TPO admin
python manage.py check --deploy          # Production config audit
python manage.py dbshell                 # Open DB shell
python manage.py shell                   # Open Django shell
```

---

*For developer documentation see [README.md](README.md)*
