from app import app, db, User

def fix_admin():
    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        if admin:
            admin.role = 'admin'
            db.session.commit()
            print("Admin role updated to 'admin'.")
        else:
            print("Admin user not found.")

if __name__ == "__main__":
    fix_admin()
