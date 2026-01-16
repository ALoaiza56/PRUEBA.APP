from flask import Flask, render_template, request, redirect, url_for, flash, Response, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from database import db, User, Student, Teacher, Grade, Attendance, SchoolDate
from datetime import datetime
import os
import csv
from io import StringIO

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secret_key_here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///school.db')
if app.config['SQLALCHEMY_DATABASE_URI'].startswith("postgres://"):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            flash('Username already exists')
        else:
            new_user = User(username=username, password_hash=generate_password_hash(password, method='scrypt'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

def create_admin_if_not_exists():
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        hashed_password = generate_password_hash('admin', method='scrypt')
        new_admin = User(username='admin', password_hash=hashed_password, role='admin')
        db.session.add(new_admin)
        db.session.commit()
        print("Admin user created.")

@app.route('/dashboard')
@login_required
def dashboard():
    students = Student.query.all()
    teachers = Teacher.query.all()
    students = Student.query.all()
    teachers = Teacher.query.all()
    
    # Filter logic
    query = Attendance.query.join(SchoolDate).join(Student)
    
    filter_date = request.args.get('filter_date')
    filter_shift = request.args.get('filter_shift')
    filter_student = request.args.get('filter_student')
    
    if filter_date:
        query = query.filter(SchoolDate.date == datetime.strptime(filter_date, '%Y-%m-%d').date())
    if filter_shift:
        query = query.filter(SchoolDate.shift == filter_shift)
    if filter_student:
         query = query.filter(Student.name.ilike(f'%{filter_student}%'))
         
    attendances = query.order_by(SchoolDate.date.desc(), SchoolDate.shift).all()
    
    school_dates = SchoolDate.query.order_by(SchoolDate.date.desc(), SchoolDate.shift).all()
    return render_template('dashboard.html', students=students, teachers=teachers, attendances=attendances, school_dates=school_dates)

@app.route('/student/add', methods=['POST'])
@login_required
def add_student():
    name = request.form.get('name')
    email = request.form.get('email')
    guardian_name = request.form.get('guardian_name')
    guardian_phone = request.form.get('guardian_phone')
    
    if name:
        existing_student = Student.query.filter_by(email=email).first()
        if existing_student and email:
            flash('El correo electrónico ya está registrado', 'error')
            return redirect(url_for('dashboard') + '#estudiantes')
            
        new_student = Student(name=name, email=email, guardian_name=guardian_name, guardian_phone=guardian_phone)
        db.session.add(new_student)
        db.session.commit()
        flash('Estudiante agregado correctamente')
    return redirect(url_for('dashboard') + '#estudiantes')

@app.route('/student/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_student(id):
    student = Student.query.get_or_404(id)
    if request.method == 'POST':
        email = request.form.get('email')
        
        # Check for duplicate email (excluding current student)
        if email:
            existing_student = Student.query.filter(Student.email == email, Student.id != id).first()
            if existing_student:
                flash('El correo electrónico ya está registrado', 'error')
                return render_template('edit_student.html', student=student)

        student.name = request.form.get('name')
        student.email = email
        student.guardian_name = request.form.get('guardian_name')
        student.guardian_phone = request.form.get('guardian_phone')
        
        db.session.commit()
        flash('Información del estudiante actualizada')
        return redirect(url_for('dashboard') + '#estudiantes')
    return render_template('edit_student.html', student=student)

@app.route('/student/delete/<int:id>')
@login_required
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash('Estudiante eliminado')
    return redirect(url_for('dashboard') + '#estudiantes')

@app.route('/teacher/add', methods=['POST'])
@login_required
def add_teacher():
    # Only admin can add teachers
    if current_user.role != 'admin':
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))

    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    password = request.form.get('password')
    
    if name and email and password:
        # Check if email exists in Teacher table
        if Teacher.query.filter_by(email=email).first():
            flash('El correo ya está registrado como profesor', 'error')
            return redirect(url_for('dashboard') + '#profesores')

        # Check if username exists in User table
        if User.query.filter_by(username=email).first():
            flash('El usuario ya existe', 'error')
            return redirect(url_for('dashboard') + '#profesores')

        # Create Teacher
        new_teacher = Teacher(name=name, email=email, phone=phone)
        db.session.add(new_teacher)
        
        # Create User for Teacher
        hashed_password = generate_password_hash(password, method='scrypt')
        new_user = User(username=email, password_hash=hashed_password, role='teacher')
        db.session.add(new_user)
        
        db.session.commit()
        flash(f'Profesor agregado correctamente.')
    return redirect(url_for('dashboard') + '#profesores')

@app.route('/teacher/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_teacher(id):
    if current_user.role != 'admin':
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))

    teacher = Teacher.query.get_or_404(id)
    if request.method == 'POST':
        teacher.name = request.form.get('name')
        # We generally don't change email as it links to User, but for now let's allow updating teacher details
        # Updating the User username is complex, so let's keep it simple for now or block email change
        # User asked to "change subject to email", implying email is the key field now.
        
        new_email = request.form.get('email')
        if new_email and new_email != teacher.email:
             # Check for uniqueness
             if Teacher.query.filter_by(email=new_email).first() or User.query.filter_by(username=new_email).first():
                 flash('El nuevo correo ya está en uso', 'error')
                 return render_template('edit_teacher.html', teacher=teacher)
             
             # Update User as well (optional but good practice)
             linked_user = User.query.filter_by(username=teacher.email).first()
             if linked_user:
                 linked_user.username = new_email
             
             teacher.email = new_email

        teacher.phone = request.form.get('phone')
        
        # Update password if provided
        new_password = request.form.get('password')
        if new_password:
             linked_user = User.query.filter_by(username=teacher.email).first()
             if linked_user:
                 linked_user.password_hash = generate_password_hash(new_password, method='scrypt')
                 flash('Contraseña actualizada')

        db.session.commit()
        flash('Información del profesor actualizada')
        return redirect(url_for('dashboard') + '#profesores')
    return render_template('edit_teacher.html', teacher=teacher)

@app.route('/teacher/delete/<int:id>')
@login_required
def delete_teacher(id):
    if current_user.role != 'admin':
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))

    teacher = Teacher.query.get_or_404(id)
    
    # Delete linked user
    linked_user = User.query.filter_by(username=teacher.email).first()
    if linked_user:
        db.session.delete(linked_user)

    db.session.delete(teacher)
    db.session.commit()
    flash('Profesor y usuario eliminados')
    return redirect(url_for('dashboard') + '#profesores')

@app.route('/attendance/add', methods=['POST'])
@login_required
def add_attendance():
    school_date_id = request.form.get('school_date_id')
    student_id = request.form.get('student_id')
    status = request.form.get('status') # 'Present', 'Absent', 'Late'
    comment = request.form.get('comment')
    
    if school_date_id and student_id and status:
        new_attendance = Attendance(
            student_id=student_id, 
            school_date_id=school_date_id, 
            status=status,
            comment=comment
        )
        db.session.add(new_attendance)
        db.session.commit()
        flash('Asistencia registrada correctamente')
    else:
        flash('Faltan datos para registrar asistencia', 'error')
        
    return redirect(url_for('dashboard') + '#asistencia')

@app.route('/attendance/export')
@login_required
def export_attendance():
    query = Attendance.query.join(SchoolDate).join(Student)
    
    filter_date = request.args.get('filter_date')
    filter_shift = request.args.get('filter_shift')
    filter_student = request.args.get('filter_student')
    
    if filter_date:
        query = query.filter(SchoolDate.date == datetime.strptime(filter_date, '%Y-%m-%d').date())
    if filter_shift:
        query = query.filter(SchoolDate.shift == filter_shift)
    if filter_student:
         query = query.filter(Student.name.ilike(f'%{filter_student}%'))
         
    attendances = query.order_by(SchoolDate.date.desc(), SchoolDate.shift).all()
    
    # Generate CSV with semicolon for better Excel compatibility in Spanish regions
    si = StringIO()
    cw = csv.writer(si, delimiter=';')
    cw.writerow(['Fecha', 'Turno', 'Estudiante', 'Estado', 'Comentario'])
    
    for record in attendances:
        cw.writerow([
            record.school_date.date, 
            record.school_date.shift, 
            record.student.name, 
            record.status, 
            record.comment or ''
        ])
        
    # Convert to UTF-8 with BOM (utf-8-sig) so Excel recognizes it correctly
    csv_data = si.getvalue().encode('utf-8-sig')
    
    output = make_response(csv_data)
    output.headers["Content-Disposition"] = "attachment; filename=asistencia_export.csv"
    output.headers["Content-type"] = "text/csv; charset=utf-8"
    return output

@app.route('/api/attendance_status/<int:school_date_id>')
@login_required
def get_attendance_status(school_date_id):
    school_date = SchoolDate.query.get_or_404(school_date_id)
    students = Student.query.all()
    
    # Get existing attendance for this date
    existing_records = {
        att.student_id: att.status 
        for att in Attendance.query.filter_by(school_date_id=school_date_id).all()
    }
    
    student_list = []
    for s in students:
        student_list.append({
            'id': s.id,
            'name': s.name,
            'status': existing_records.get(s.id, 'Presente') # Default to Presente if no record
        })
        
    return {'students': student_list}

@app.route('/attendance/bulk_add', methods=['POST'])
@login_required
def bulk_add_attendance():
    school_date_id = request.form.get('school_date_id')
    
    if not school_date_id:
        flash('Error: Fecha no seleccionada', 'error')
        return redirect(url_for('dashboard') + '#asistencia')

    student_ids = request.form.getlist('student_ids')
    
    # Clear existing for this date/shift to avoid complex upsert logic for now, 
    # or just update/insert. Let's do update/insert check.
    
    count = 0
    for s_id in student_ids:
        status = request.form.get(f'status_{s_id}')
        if status:
            # Check exist
            att = Attendance.query.filter_by(school_date_id=school_date_id, student_id=s_id).first()
            if att:
                att.status = status
            else:
                new_att = Attendance(
                    school_date_id=school_date_id,
                    student_id=s_id,
                    status=status
                )
                db.session.add(new_att)
            count += 1
            
    db.session.commit()
    flash(f'Asistencia actualizada para {count} estudiantes')
    return redirect(url_for('dashboard') + '#asistencia')

@app.route('/date/add', methods=['POST'])
@login_required
def add_school_date():
    if current_user.role != 'admin':
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))

    date_str = request.form.get('date')
    shift = request.form.get('shift')
    
    if date_str and shift:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Check uniqueness
        exists = SchoolDate.query.filter_by(date=date_obj, shift=shift).first()
        if exists:
            flash(f'La fecha {date_str} con turno {shift} ya existe', 'error')
            return redirect(url_for('dashboard') + '#fechas')
            
        new_date = SchoolDate(date=date_obj, shift=shift)
        db.session.add(new_date)
        db.session.commit()
        flash('Fecha y turno agregados correctamente')
    return redirect(url_for('dashboard') + '#fechas')

@app.route('/date/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_school_date(id):
    if current_user.role != 'admin':
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))

    school_date = SchoolDate.query.get_or_404(id)
    if request.method == 'POST':
        date_str = request.form.get('date')
        shift = request.form.get('shift')
        
        if date_str and shift:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Check uniqueness if changed
            if date_obj != school_date.date or shift != school_date.shift:
                exists = SchoolDate.query.filter_by(date=date_obj, shift=shift).first()
                if exists:
                    flash(f'La fecha {date_str} con turno {shift} ya existe', 'error')
                    return render_template('edit_date.html', school_date=school_date)
            
            school_date.date = date_obj
            school_date.shift = shift
            db.session.commit()
            flash('Fecha actualizada')
            return redirect(url_for('dashboard') + '#fechas')
            
    return render_template('edit_date.html', school_date=school_date)

@app.route('/date/delete/<int:id>')
@login_required
def delete_school_date(id):
    if current_user.role != 'admin':
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))

    school_date = SchoolDate.query.get_or_404(id)
    db.session.delete(school_date)
    db.session.commit()
    flash('Fecha eliminada')
    return redirect(url_for('dashboard') + '#fechas')

@app.route('/attendance/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_attendance(id):
    attendance = Attendance.query.get_or_404(id)
    if request.method == 'POST':
        attendance.status = request.form.get('status')
        attendance.comment = request.form.get('comment')
        db.session.commit()
        flash('Asistencia actualizada')
        return redirect(url_for('dashboard') + '#asistencia')
    return render_template('edit_attendance.html', attendance=attendance)

@app.route('/attendance/delete/<int:id>')
@login_required
def delete_attendance(id):
    attendance = Attendance.query.get_or_404(id)
    db.session.delete(attendance)
    db.session.commit()
    flash('Registro de asistencia eliminado')
    return redirect(url_for('dashboard') + '#asistencia')

# Create tables and admin user
with app.app_context():
    db.create_all()
    create_admin_if_not_exists()

if __name__ == '__main__':
    app.run(debug=True)
