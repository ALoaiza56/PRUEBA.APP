from app import app, db, SchoolDate
from datetime import date

def verify_dates():
    with app.app_context():
        # 1. Clean up potential previous test data
        existing = SchoolDate.query.filter_by(date=date(2026, 1, 20), shift='Mañana (10-12am)').first()
        if existing:
            db.session.delete(existing)
            db.session.commit()
            
        # 2. Add verification
        new_date = SchoolDate(date=date(2026, 1, 20), shift='Mañana (10-12am)')
        db.session.add(new_date)
        db.session.commit()
        
        # 3. Read verification
        fetched = SchoolDate.query.filter_by(date=date(2026, 1, 20)).first()
        if fetched and fetched.shift == 'Mañana (10-12am)':
            print("PASS: Date created and retrieved.")
        else:
            print("FAIL: Date creation/retrieval failed.")

if __name__ == "__main__":
    verify_dates()
