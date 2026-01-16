from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(20), default='teacher') # 'admin' or 'teacher'

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=True)
    guardian_name = db.Column(db.String(150), nullable=True)
    guardian_phone = db.Column(db.String(20), nullable=True)
    grades = db.relationship('Grade', backref='student', lazy=True)
    attendance_records = db.relationship('Attendance', backref='student', lazy=True)

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)

class SchoolDate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    shift = db.Column(db.String(50), nullable=False)
    __table_args__ = (db.UniqueConstraint('date', 'shift', name='_date_shift_uc'),)

class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Float, nullable=False)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    school_date_id = db.Column(db.Integer, db.ForeignKey('school_date.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False) # 'Present', 'Absent', 'Late'
    comment = db.Column(db.String(200), nullable=True)
    school_date = db.relationship('SchoolDate', backref='attendances')
