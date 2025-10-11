# Resume Bank Management System for College TPO

A web-based application for managing student resumes and placement data for College Training & Placement Officers (TPO).

## 🎯 Project Overview

This system allows students to register, upload resumes, and update their placement status, while TPOs can view, filter, and manage student data with analytics and export capabilities.

## 🚀 Features

### Student Module
- Student registration and login
- Profile management (Name, Roll No, Email, Branch, CGPA, Skills)
- Resume upload (PDF only)
- Profile and resume editing
- Placement status updates

### Admin (TPO) Module
- Secure admin login
- View all student profiles
- Advanced filtering and search
- Resume download (individual and bulk)
- CSV export functionality
- Placement status management
- Analytics dashboard with charts

## 🛠 Tech Stack

- **Backend**: Python Django 4.2
- **Database**: MySQL (via XAMPP)
- **Frontend**: HTML, CSS (Bootstrap 5), JavaScript
- **Charts**: Chart.js
- **File Handling**: Django file uploads
- **CSV Export**: Python csv module

## 📋 Prerequisites

Before running this project, make sure you have:

1. **Python 3.8+** installed
2. **XAMPP** installed and running (for MySQL)
3. **Git** (optional, for version control)

## 🚀 Installation & Setup

### Step 1: Clone/Download the Project
```bash
# If using git
git clone <repository-url>
cd TNPHelper

# Or simply download and extract the project files
```

### Step 2: Set Up Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Database
1. Start XAMPP and ensure MySQL service is running
2. Open phpMyAdmin (http://localhost/phpmyadmin)
3. Create a new database named `resume_bank_db`
4. Update database settings in `resume_bank/settings.py` if needed

### Step 5: Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Create Superuser (Admin)
```bash
python manage.py createsuperuser
# Follow the prompts to create admin account
```

### Step 7: Run the Development Server
```bash
python manage.py runserver
```

## 🌐 Access the Application

- **Main Application**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **Student Portal**: http://127.0.0.1:8000/student/
- **TPO Portal**: http://127.0.0.1:8000/tpo/

## 👥 Sample Accounts

### Admin Account
- Username: `admin`
- Password: `admin123`

### Sample Student Accounts
- Username: `student1`, Password: `student123`
- Username: `student2`, Password: `student123`

## 📁 Project Structure

```
TNPHelper/
├── resume_bank/          # Main Django project
│   ├── settings.py       # Project settings
│   ├── urls.py          # Main URL configuration
│   └── wsgi.py          # WSGI configuration
├── students/            # Student app
│   ├── models.py        # Database models
│   ├── views.py         # View functions
│   ├── forms.py         # Forms
│   └── templates/       # HTML templates
├── tpo/                 # TPO app
│   ├── views.py         # TPO views
│   ├── forms.py         # TPO forms
│   └── templates/       # TPO templates
├── static/              # Static files (CSS, JS, images)
├── media/               # Uploaded files (resumes)
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🔧 Configuration

### Database Settings
The project is configured to use MySQL. Update `resume_bank/settings.py` if you need to change database settings:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'resume_bank_db',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### File Upload Settings
- Resume files are stored in `media/resumes/`
- Maximum file size: 10MB
- Allowed formats: PDF only

## 🎨 Customization

### Styling
- Bootstrap 5 is used for responsive design
- Custom CSS can be added in `static/css/style.css`
- Chart.js is used for analytics dashboard

### Adding New Fields
To add new fields to student profiles:
1. Update `students/models.py`
2. Run `python manage.py makemigrations`
3. Run `python manage.py migrate`
4. Update forms and templates accordingly

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure XAMPP MySQL service is running
   - Check database name and credentials in settings.py

2. **Migration Errors**
   - Delete all files in `students/migrations/` (except `__init__.py`)
   - Run `python manage.py makemigrations` again

3. **Static Files Not Loading**
   - Run `python manage.py collectstatic`
   - Check `STATIC_URL` and `STATICFILES_DIRS` in settings.py

4. **File Upload Issues**
   - Ensure `media/` directory exists and is writable
   - Check file size limits in settings.py

## 📝 Development Notes

- The project uses Django's built-in authentication system
- File uploads are handled securely with validation
- CSRF protection is enabled by default
- The admin panel provides additional management capabilities

## 🤝 Contributing

This is a beginner-friendly project. Feel free to:
- Add new features
- Improve the UI/UX
- Fix bugs
- Add more validation rules

## 📄 License

This project is created for educational purposes.

## 👨‍💻 Team

This project is designed for 2-3 beginner developers working on their final year Computer Science engineering project.

---

**Happy Coding! 🚀** 