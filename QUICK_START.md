# Quick Start Guide - Resume Bank Management System

## 🚀 Quick Setup (5 minutes)

### Prerequisites
- Python 3.8+ installed
- XAMPP installed and running (for MySQL)

### Step 1: Database Setup
1. Start XAMPP and ensure MySQL service is running
2. Open phpMyAdmin: http://localhost/phpmyadmin
3. Create a new database named `resume_bank_db`

### Step 2: Project Setup
```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations
python manage.py makemigrations
python manage.py migrate

# 5. Create sample data
python setup.py

# 6. Run the server
python manage.py runserver
```

### Step 3: Access the Application
- **Main Application**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **Student Portal**: http://127.0.0.1:8000/student/
- **TPO Portal**: http://127.0.0.1:8000/tpo/

## 👥 Sample Accounts

### Admin Account
- **Username**: `admin`
- **Password**: `admin123`

### Sample Student Accounts
- **Student 1**: `student1@example.com` / `student123`
- **Student 2**: `student2@example.com` / `student123`
- **Student 3**: `student3@example.com` / `student123`
- **Student 4**: `student4@example.com` / `student123`
- **Student 5**: `student5@example.com` / `student123`

## 🎯 Quick Test

1. **Test Student Registration**:
   - Go to http://127.0.0.1:8000/student/register/
   - Create a new student account
   - Login and upload a resume

2. **Test TPO Dashboard**:
   - Login as admin: http://127.0.0.1:8000/tpo/login/
   - View student list and analytics
   - Test filtering and export features

3. **Test Analytics**:
   - Go to Analytics dashboard
   - View charts and statistics

## 🛠 Troubleshooting

### Common Issues

1. **Database Connection Error**
   ```bash
   # SQLite3 is used by default and requires no setup
   # If using MySQL, ensure XAMPP MySQL is running
   # Check database name in settings.py
   ```

2. **Migration Errors**
   ```bash
   # Delete migrations folder and recreate
   rm -rf students/migrations/*
   rm -rf tpo/migrations/*
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Static Files Not Loading**
   ```bash
   python manage.py collectstatic
   ```

## 📁 Project Structure
```
TNPHelper/
├── resume_bank/          # Main Django project
├── students/            # Student management app
├── tpo/                 # TPO management app
├── templates/           # HTML templates
├── static/              # Static files
├── media/               # Uploaded files
├── requirements.txt     # Dependencies
├── setup.py            # Setup script
└── README.md           # Full documentation
```

## 🎉 Success!
Your Resume Bank Management System is now running! 

- Students can register, upload resumes, and update profiles
- TPOs can manage students, view analytics, and export data
- All features are fully functional and ready for use

For detailed documentation, see `README.md` 