from app import app, db, SchoolDate, Student, Attendance
from datetime import date

def verify_attendance_features():
    with app.app_context():
        # Setup data
        s_date = SchoolDate.query.filter_by(date=date(2025, 12, 1)).first()
        if not s_date:
            s_date = SchoolDate(date=date(2025, 12, 1), shift='Mañana (10-12am)')
            db.session.add(s_date)
            db.session.commit()
            
        student = Student.query.first()
        if not student:
            print("SKIP: No students found to test attendance.")
            return

        # 1. Test Add Attendance
        # Check if already exists to avoid dupes in this simplistic test
        exists = Attendance.query.filter_by(school_date_id=s_date.id, student_id=student.id).first()
        if not exists:
            att = Attendance(
                student_id=student.id,
                school_date_id=s_date.id,
                status='Presente',
                comment='Test Comment'
            )
            db.session.add(att)
            db.session.commit()
            print("PASS: Added attendance record.")
        else:
             print("INFO: Attendance record already exists.")

        # 2. Test Query/Filter (Simulation)
        # Filter by date
        results = Attendance.query.join(SchoolDate).filter(SchoolDate.date == date(2025, 12, 1)).all()
        if results:
            print(f"PASS: Filter by date found {len(results)} records.")
        else:
            print("FAIL: Filter by date found 0 records.")

        # 3. Test Comment retrieval
        rec = Attendance.query.filter_by(comment='Test Comment').first()
        if rec and rec.comment == 'Test Comment':
             print("PASS: Comment saved and retrieved.")
        else:
             print("FAIL: Comment not found.")
             
        # 4. Test joined fields
        if rec and rec.school_date.shift == 'Mañana (10-12am)':
            print("PASS: Linked SchoolDate shift verified.")
        else:
            print("FAIL: SchoolDate linkage issue.")

if __name__ == "__main__":
    verify_attendance_features()
