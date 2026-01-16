from app import app, db, User, Teacher, create_admin_if_not_exists

def verify():
    with app.app_context():
        # 1. Trigger admin creation
        create_admin_if_not_exists()
        
        # 2. Check Admin
        admin = User.query.filter_by(username='admin').first()
        if admin and admin.role == 'admin':
            print("PASS: Admin user exists with correct role.")
        else:
            print("FAIL: Admin user missing or incorrect role.")

        # 3. Simulate adding a teacher (Validation of logic, not route)
        test_email = 'verify_teacher@test.com'
        if not Teacher.query.filter_by(email=test_email).first():
            print(f"Adding test teacher: {test_email}")
            # Logic similar to route
            from werkzeug.security import generate_password_hash
            
            t = Teacher(name="Test Teacher", email=test_email, phone="555")
            db.session.add(t)
            
            u = User(username=test_email, password_hash=generate_password_hash('123456', method='scrypt'), role='teacher')
            db.session.add(u)
            db.session.commit()
        
        # 4. Verify Teacher User
        teacher_user = User.query.filter_by(username=test_email).first()
        if teacher_user and teacher_user.role == 'teacher':
             print("PASS: Teacher user created with correct role.")
        else:
             print("FAIL: Teacher user not found or incorrect role.")

if __name__ == "__main__":
    verify()
