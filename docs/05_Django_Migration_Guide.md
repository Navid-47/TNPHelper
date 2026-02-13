# Django + MySQL Migration Guide
## Flask (MongoDB) → Django (MySQL) — Step-by-Step

| Field | Value |
|-------|-------|
| **Date** | 2026-02-13 |
| **Source** | Flask 3.x + PyMongo + MongoDB |
| **Target** | Django 5.x + MySQL 8.x |

---

## Phase 1: Project Scaffolding (Day 1)

### 1.1 Create Django Project
```bash
# Create project directory
mkdir tnp_django && cd tnp_django

# Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Linux/Mac

# Install Django & MySQL connector
pip install django mysqlclient python-dotenv django-widget-tweaks

# Create Django project
django-admin startproject tnp_project .

# Create apps
python manage.py startapp accounts
python manage.py startapp students
python manage.py startapp tpo
python manage.py startapp core
```

### 1.2 Configure `settings.py`

```python
# tnp_project/settings.py

import os
from dotenv import load_dotenv
load_dotenv()

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'widget_tweaks',
    # Project apps
    'accounts',
    'students',
    'tpo',
    'core',
]

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'tnp_db'),
        'USER': os.getenv('DB_USER', 'root'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

# File uploads
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# Static
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Auth
LOGIN_URL = '/auth/student/login'
LOGIN_REDIRECT_URL = '/student/dashboard'
LOGOUT_REDIRECT_URL = '/'
```

### 1.3 Create `.env`
```env
SECRET_KEY=your-django-secret-key-change-in-production
DB_NAME=tnp_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
```

### 1.4 Create MySQL Database
```sql
CREATE DATABASE tnp_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

## Phase 2: Models (Day 1-2)

### File-by-File Migration Map

| Flask File | Django File | Key Changes |
|-----------|-------------|-------------|
| `app/models/user.py` | `accounts/models.py` | Replace manual PyMongo with `AbstractUser` |
| `app/models/student.py` | `students/models.py` | Replace PyMongo queries with Django ORM |
| *(drives in routes)* | `tpo/models.py` | New `Drive` and `Application` models |

### Key Differences

| Flask (PyMongo) | Django ORM |
|----------------|------------|
| `db.users.find_one({'email': email})` | `User.objects.get(email=email)` |
| `db.students.insert_one(doc)` | `Student.objects.create(**data)` |
| `db.students.update_one({..}, {'$set': data})` | `student.field = val; student.save()` |
| `db.students.count_documents(query)` | `Student.objects.filter(**q).count()` |
| `bcrypt.generate_password_hash(pw)` | `User.objects.create_user(password=pw)` |
| `bcrypt.check_password_hash(hash, pw)` | `user.check_password(pw)` |
| Manual `ObjectId` handling | Auto-increment `id` PK |

### Run Migrations
```bash
python manage.py makemigrations accounts students tpo
python manage.py migrate
```

---

## Phase 3: Forms (Day 2)

### Migration Map

| Flask File | Django File |
|-----------|-------------|
| `app/forms/auth_forms.py` | `accounts/forms.py` |
| `app/forms/student_forms.py` | `students/forms.py` |
| `app/forms/tpo_forms.py` | `tpo/forms.py` |

### Key Differences

| Flask-WTF | Django Forms |
|-----------|--------------|
| `FlaskForm` | `forms.Form` or `forms.ModelForm` |
| `StringField` | `forms.CharField` |
| `PasswordField` | `forms.CharField(widget=PasswordInput)` |
| `SelectField(choices=[...])` | `forms.ChoiceField(choices=[...])` |
| `DecimalField` | `forms.DecimalField` |
| `FileField + FileAllowed` | `forms.FileField` + `FileExtensionValidator` |
| `DataRequired()` | `required=True` (default) |
| `form.validate_on_submit()` | `form.is_valid()` |
| `form.email.data` | `form.cleaned_data['email']` |

---

## Phase 4: Views (Day 2-3)

### Migration Map

| Flask File | Django File |
|-----------|-------------|
| `app/routes/main.py` | `core/views.py` |
| `app/routes/auth.py` | `accounts/views.py` |
| `app/routes/student.py` | `students/views.py` |
| `app/routes/tpo.py` | `tpo/views.py` |

### Key Differences

| Flask | Django |
|-------|--------|
| `@bp.route('/path', methods=['GET','POST'])` | `path('path/', view_func)` in `urls.py` |
| `redirect(url_for('bp.view'))` | `redirect(reverse('namespace:view'))` |
| `flash('msg', 'category')` | `messages.success(request, 'msg')` |
| `render_template('tpl.html', ctx)` | `render(request, 'tpl.html', ctx)` |
| `request.args.get('key')` | `request.GET.get('key')` |
| `request.form.get('key')` | `request.POST.get('key')` |
| `send_file(path)` | `FileResponse(path)` |
| `@login_required` (Flask-Login) | `@login_required` (django.contrib.auth) |
| Custom `@admin_required` | Custom decorator or `UserPassesTestMixin` |

---

## Phase 5: URL Configuration (Day 3)

### `tnp_project/urls.py`
```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('auth/', include('accounts.urls')),
    path('student/', include('students.urls')),
    path('tpo/', include('tpo.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## Phase 6: Templates (Day 3-4)

### Template Migration

| Change | Details |
|--------|---------|
| Template engine | Jinja2 → Django Template Language |
| `{{ url_for('bp.view') }}` | `{% url 'namespace:view' %}` |
| `{{ form.hidden_tag() }}` | `{% csrf_token %}` |
| `{{ form.field() }}` | `{{ form.field }}` or `{{ form.field|add_class:"form-control" }}` |
| `{% with messages = get_flashed_messages() %}` | `{% for message in messages %}` (Django messages) |
| Static files | `{{ url_for('static', filename='css/style.css') }}` → `{% static 'css/style.css' %}` |

> **Tip**: Most HTML structure, Bootstrap classes, and Chart.js code can be reused as-is. Only template tags need updating.

---

## Phase 7: Utilities (Day 4)

### Migration Map

| Flask File | Django File | Notes |
|-----------|-------------|-------|
| `app/utils/decorators.py` | `accounts/decorators.py` | `flask_login` → `django.contrib.auth` |
| `app/utils/helpers.py` | `tpo/utils.py` | `current_app.root_path` → `settings.MEDIA_ROOT` |

### Decorators
```python
# Flask
from flask_login import current_user

# Django
from django.contrib.auth.decorators import login_required
def admin_required(view_func):
    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_admin:
            messages.error(request, 'Permission denied.')
            return redirect('core:home')
        return view_func(request, *args, **kwargs)
    return wrapper
```

---

## Phase 8: Create Admin & Seed Data (Day 4)

### Create Superuser
```bash
python manage.py createsuperuser
# Email: admin@gmail.com
# Password: admin123
```

### Management Command (Optional)
```bash
python manage.py shell
>>> from accounts.models import User
>>> user = User.objects.create_user(username='admin@gmail.com', email='admin@gmail.com', password='admin123', role='admin')
```

---

## Phase 9: Testing & Verification (Day 5)

### Checklist
- [ ] MySQL database created and connected
- [ ] All migrations run successfully
- [ ] Admin user created
- [ ] Landing page loads at `/`
- [ ] Student registration flow works
- [ ] Student login/logout works
- [ ] Student dashboard shows profile
- [ ] Profile edit saves to MySQL
- [ ] Resume upload stores file in `media/resumes/`
- [ ] TPO login works
- [ ] TPO dashboard lists students with filters
- [ ] Pagination works (20/page)
- [ ] Sorting works (all 8 options)
- [ ] Student detail page loads
- [ ] Placement status update saves
- [ ] CSV export downloads correctly
- [ ] Bulk ZIP download works
- [ ] Analytics charts render with correct data
- [ ] Drive creation works
- [ ] Student can view and apply to drives
- [ ] Drive applicants page shows applications
- [ ] Application status updates work
- [ ] Django admin panel accessible at `/admin/`

---

## Summary Timeline

| Phase | Task | Duration |
|-------|------|----------|
| 1 | Project scaffolding + MySQL setup | Day 1 |
| 2 | Models + migrations | Day 1-2 |
| 3 | Forms | Day 2 |
| 4 | Views (auth, student, tpo) | Day 2-3 |
| 5 | URL configuration | Day 3 |
| 6 | Template migration | Day 3-4 |
| 7 | Utilities + decorators | Day 4 |
| 8 | Admin + seed data | Day 4 |
| 9 | Testing + verification | Day 5 |
| **Total** | | **~5 working days** |
