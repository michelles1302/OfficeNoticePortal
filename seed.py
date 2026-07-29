import os
from app import create_app
from app.extensions import db
from app.models.role import Role
from app.models.department import Department
from app.models.notice_category import NoticeCategory
from app.models.user import User

# Instantiate application context to interact with the database
app = create_app(os.environ.get('FLASK_ENV', 'development'))

def seed_database():
    """
    Seeds default Roles, Departments, Notice Categories, 
    and a default Super Admin account.
    """
    print("Initializing Database Seeding...")
    
    # Ensure tables exist
    db.create_all()
    
    # 1. Seed Roles
    roles_data = [
        ('Super Admin', 'Full system access, manages users, departments, and system configurations.'),
        ('Department Admin', 'Can manage notice creation, categories, and target notices to their department.'),
        ('Employee', 'Can view corporate notice feed, download attachments, and acknowledge notices.')
    ]
    
    roles = {}
    for name, desc in roles_data:
        role = Role.query.filter_by(name=name).first()
        if not role:
            role = Role(name=name, description=desc)
            db.session.add(role)
            db.session.flush()  # Flushes to db to generate PK IDs for foreign keys
            print(f"Added Role: {name}")
        else:
            print(f"Role already exists: {name}")
        roles[name] = role
        
    # 2. Seed Departments
    depts_data = [
        ('Human Resources', 'HR'),
        ('Finance & Accounting', 'FIN'),
        ('Information Technology', 'IT'),
        ('Marketing & Sales', 'MKT'),
        ('Operations', 'OPS')
    ]
    
    departments = {}
    for name, code in depts_data:
        dept = Department.query.filter_by(code=code).first()
        if not dept:
            dept = Department(name=name, code=code)
            db.session.add(dept)
            db.session.flush()  # Flushes to db to generate PK IDs
            print(f"Added Department: {name} ({code})")
        else:
            print(f"Department already exists: {name} ({code})")
        departments[code] = dept
        
    # 3. Seed Notice Categories
    categories_data = [
        ('General', 'General announcements and updates.'),
        ('Policy', 'Formal organizational policy modifications and updates.'),
        ('Meeting', 'Schedules, notes, and notices regarding meetings.'),
        ('Holiday', 'Corporate holidays and office closure announcements.'),
        ('Training', 'Training opportunities, guidelines, and compliance requirements.'),
        ('Safety', 'Safety instructions, drills, and emergency procedures.')
    ]
    
    for name, desc in categories_data:
        cat = NoticeCategory.query.filter_by(name=name).first()
        if not cat:
            cat = NoticeCategory(name=name, description=desc)
            db.session.add(cat)
            print(f"Added Category: {name}")
        else:
            print(f"Category already exists: {name}")
            
    # 4. Seed Default Super Admin Account
    admin_username = 'superadmin'
    admin_email = 'admin@noticeportal.com'
    admin_pass = 'AdminPassword123'
    
    super_admin_role = roles['Super Admin']
    it_dept = departments['IT']
    
    admin_user = User.query.filter_by(email=admin_email).first()
    if not admin_user:
        admin_user = User(
            username=admin_username,
            email=admin_email,
            password=admin_pass,
            role_id=super_admin_role.id,
            department_id=it_dept.id
        )
        db.session.add(admin_user)
        print(f"Created default Super Admin User: {admin_username} ({admin_email})")
    else:
        print(f"Super Admin user already exists: {admin_email}")
        
    db.session.commit()
    print("Database seeding completed successfully!")

if __name__ == '__main__':
    with app.app_context():
        seed_database()
