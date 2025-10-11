#!/usr/bin/env python
"""
Setup script for Resume Bank Management System.
This script helps with initial project setup and sample data creation.
"""
import os
import sys
import django

def setup_django():
    """Setup Django environment."""
    # Add the project directory to Python path
    project_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_dir)
    
    # Set Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resume_bank.settings')
    
    # Configure Django
    django.setup()

def create_sample_data():
    """Create sample students and admin user."""
    from django.contrib.auth.models import User
    from students.models import Student
    
    print("Creating sample data...")
    
    # Create admin user
    if not User.objects.filter(username='admin').exists():
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            is_staff=True,
            is_superuser=True
        )
        print("✓ Admin user created (username: admin, password: admin123)")
    else:
        print("✓ Admin user already exists")
    
    # Create sample students
    sample_students = [
        {
            'username': 'student1@example.com',
            'email': 'student1@example.com',
            'password': 'student123',
            'name': 'John Doe',
            'roll_no': '2021001',
            'branch': 'CSE',
            'cgpa': 8.5,
            'skills': 'Python, Java, Machine Learning, Web Development',
            'placement_status': 'placed',
            'company_name': 'Tech Corp',
            'package': 12.5
        },
        {
            'username': 'student2@example.com',
            'email': 'student2@example.com',
            'password': 'student123',
            'name': 'Jane Smith',
            'roll_no': '2021002',
            'branch': 'ECE',
            'cgpa': 9.2,
            'skills': 'VLSI, Embedded Systems, C++, Python',
            'placement_status': 'placed',
            'company_name': 'Electronics Inc',
            'package': 15.0
        },
        {
            'username': 'student3@example.com',
            'email': 'student3@example.com',
            'password': 'student123',
            'name': 'Mike Johnson',
            'roll_no': '2021003',
            'branch': 'ME',
            'cgpa': 7.8,
            'skills': 'AutoCAD, SolidWorks, Manufacturing, CAD',
            'placement_status': 'in_process',
            'company_name': '',
            'package': None
        },
        {
            'username': 'student4@example.com',
            'email': 'student4@example.com',
            'password': 'student123',
            'name': 'Sarah Wilson',
            'roll_no': '2021004',
            'branch': 'CSE',
            'cgpa': 8.9,
            'skills': 'JavaScript, React, Node.js, MongoDB',
            'placement_status': 'not_placed',
            'company_name': '',
            'package': None
        },
        {
            'username': 'student5@example.com',
            'email': 'student5@example.com',
            'password': 'student123',
            'name': 'David Brown',
            'roll_no': '2021005',
            'branch': 'IT',
            'cgpa': 8.1,
            'skills': 'Data Science, SQL, Python, Tableau',
            'placement_status': 'placed',
            'company_name': 'Data Analytics Ltd',
            'package': 14.0
        }
    ]
    
    for student_data in sample_students:
        if not User.objects.filter(username=student_data['username']).exists():
            # Create user
            user = User.objects.create_user(
                username=student_data['username'],
                email=student_data['email'],
                password=student_data['password'],
                first_name=student_data['name'].split()[0],
                last_name=student_data['name'].split()[1] if len(student_data['name'].split()) > 1 else ''
            )
            
            # Create student profile
            Student.objects.create(
                user=user,
                name=student_data['name'],
                roll_no=student_data['roll_no'],
                email=student_data['email'],
                branch=student_data['branch'],
                cgpa=student_data['cgpa'],
                skills=student_data['skills'],
                placement_status=student_data['placement_status'],
                company_name=student_data['company_name'],
                package=student_data['package']
            )
            print(f"✓ Student created: {student_data['name']} ({student_data['username']})")
        else:
            print(f"✓ Student already exists: {student_data['name']}")
    
    print("\nSample data creation completed!")
    print("\nSample Accounts:")
    print("Admin: username=admin, password=admin123")
    print("Students: username=student1@example.com to student5@example.com, password=student123")

def main():
    """Main setup function."""
    print("Resume Bank Management System - Setup")
    print("=" * 50)
    
    try:
        setup_django()
        print("✓ Django environment setup completed")
        
        # Check if database is migrated
        try:
            from students.models import Student
            Student.objects.count()
            print("✓ Database connection verified")
        except Exception as e:
            print("✗ Database not migrated. Please run migrations first:")
            print("  python manage.py makemigrations")
            print("  python manage.py migrate")
            return
        
        # Create sample data
        create_sample_data()
        
        print("\n" + "=" * 50)
        print("Setup completed successfully!")
        print("\nNext steps:")
        print("1. Run the development server: python manage.py runserver")
        print("2. Access the application at: http://127.0.0.1:8000/")
        print("3. Login with the sample accounts provided above")
        
    except Exception as e:
        print(f"✗ Setup failed: {str(e)}")
        print("\nPlease ensure:")
        print("1. All dependencies are installed: pip install -r requirements.txt")
        print("2. Database is configured and running")
        print("3. Migrations are applied")

if __name__ == '__main__':
    main() 