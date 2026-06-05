import os
import json
import base64
import io
from PIL import Image
import numpy as np
import cv2
import face_recognition
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, Teacher, Student, Attendance

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback-dev-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Teacher.query.get(int(user_id))

# Initialize Database on first run
with app.app_context():
    db.create_all()

# Helper function to convert base64 image to RGB frame
def base64_to_rgb_frame(base64_string):
    encoded_data = base64_string.split(',')[1]
    image_data = base64.b64decode(encoded_data)
    image = Image.open(io.BytesIO(image_data)).convert("RGB")
    return np.array(image)

# --- AUTHENTICATION ROUTES ---
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = Teacher.query.filter_by(username=username).first()
        if user:
            flash('Username already exists.')
            return redirect(url_for('signup'))
            
        new_user = Teacher(username=username, password_hash=generate_password_hash(password, method='scrypt'))
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully! Please log in.')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = Teacher.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        
        flash('Please check your login details and try again.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# --- ADMIN DASHBOARD ---
@app.route('/dashboard')
@login_required
def dashboard():
    today = datetime.now().date()
    now = datetime.now().time()
    
    date_str = request.args.get('date')
    if date_str:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        target_date = today
        
    # Time Strictness Schedule
    from datetime import time
    schedule = {
        'PECS': (time(11, 30), time(12, 30)),
        'SE': (time(12, 30), time(13, 30)),
        'AIML': (time(14, 0), time(15, 0)),
        'DAA': (time(15, 0), time(16, 0)),
        'CD': (time(16, 0), time(17, 0)),
        'CNA': (time(17, 0), time(18, 0))
    }
    
    # Determine the default active subject based on current time
    default_subject = 'All'
    if target_date == today:
        for subj, (start_time, end_time) in schedule.items():
            if start_time <= now <= end_time:
                default_subject = subj
                break
            
    selected_subject = request.args.get('subject', default_subject)
    total_students = Student.query.count()
    
    if selected_subject == 'All':
        present_records = Attendance.query.join(Student).filter(Attendance.date == target_date).order_by(Student.prn.asc()).all()
        # For 'All', present_today counts unique students present today across all subjects
        present_today = db.session.query(Attendance.student_id).filter_by(date=target_date).distinct().count()
    else:
        present_records = Attendance.query.join(Student).filter(Attendance.date == target_date, Attendance.subject == selected_subject).order_by(Student.prn.asc()).all()
        present_today = len(present_records)
        
    absent_today = total_students - present_today if total_students > present_today else 0
    display_date = "Today" if target_date == today else target_date.strftime('%b %d, %Y')
    
    return render_template('dashboard.html', 
                           total=total_students, 
                           present=present_today, 
                           absent=absent_today,
                           present_records=present_records,
                           selected_subject=selected_subject,
                           selected_date=target_date.strftime('%Y-%m-%d'),
                           display_date=display_date)

@app.route('/delete_attendance/<int:id>', methods=['POST'])
@login_required
def delete_attendance(id):
    record = Attendance.query.get_or_404(id)
    db.session.delete(record)
    db.session.commit()
    return redirect(request.referrer or url_for('dashboard'))

@app.route('/delete_student/<int:id>', methods=['POST'])
@login_required
def delete_student(id):
    student = Student.query.get_or_404(id)
    Attendance.query.filter_by(student_id=student.id).delete()
    db.session.delete(student)
    db.session.commit()
    return redirect(request.referrer or url_for('students_list'))

@app.route('/analytics')
@login_required
def analytics():
    from sqlalchemy import func
    # 1. High-level stats
    total_students = Student.query.count()
    total_records = Attendance.query.count()
    today = datetime.now().date()
    today_present = db.session.query(Attendance.student_id).filter_by(date=today).distinct().count()
    
    # 2. Subject-wise Distribution
    subject_counts = db.session.query(Attendance.subject, func.count(Attendance.id)).group_by(Attendance.subject).all()
    subjects = [s[0] for s in subject_counts]
    sub_counts = [s[1] for s in subject_counts]
    
    return render_template('analytics.html', 
                           total_students=total_students,
                           total_records=total_records,
                           today_present=today_present,
                           subjects=subjects,
                           sub_counts=sub_counts)

@app.route('/students')
@login_required
def students_list():
    query = request.args.get('q', '')
    if query:
        students = Student.query.filter((Student.name.ilike(f'%{query}%')) | (Student.prn.ilike(f'%{query}%'))).order_by(Student.prn.asc()).all()
    else:
        students = Student.query.order_by(Student.prn.asc()).all()
    return render_template('students_list.html', students=students, query=query)

@app.route('/add_student')
@login_required
def add_student():
    return render_template('add_student.html')

@app.route('/export_csv')
@login_required
def export_csv():
    import csv
    from flask import Response
    
    selected_subject = request.args.get('subject', 'All')
    date_str = request.args.get('date')
    if date_str:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        target_date = datetime.now().date()
    
    if selected_subject == 'All':
        records = Attendance.query.join(Student).filter(Attendance.date == target_date).order_by(Student.prn.asc()).all()
        filename = f"Attendance_All_{target_date}.csv"
    else:
        records = Attendance.query.join(Student).filter(Attendance.date == target_date, Attendance.subject == selected_subject).order_by(Student.prn.asc()).all()
        filename = f"Attendance_{selected_subject}_{target_date}.csv"
        
    import io
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Time', 'PRN', 'Name', 'Subject', 'Status'])
    
    for r in records:
        writer.writerow([
            r.date.strftime('%Y-%m-%d'),
            r.time.strftime('%H:%M:%S'),
            r.student.prn,
            r.student.name,
            r.subject,
            r.status
        ])

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )

# --- API ROUTES FOR WEBCAM ---
@app.route('/api/enroll', methods=['POST'])
@login_required
def api_enroll():
    data = request.json
    name = data.get('name')
    prn = data.get('prn')
    phone = data.get('phone')
    image_data = data.get('image')
    
    if Student.query.filter_by(prn=prn).first():
        return jsonify({'error': 'Student with this PRN already exists!'}), 400
        
    rgb_frame = base64_to_rgb_frame(image_data)
    
    # Extract face encoding
    face_locations = face_recognition.face_locations(rgb_frame)
    if not face_locations:
        return jsonify({'error': 'No face found in the image. Please try again.'}), 400
        
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
    encoding_json = json.dumps(face_encodings[0].tolist())
    
    new_student = Student(name=name, prn=prn, phone=phone, face_encoding=encoding_json)
    db.session.add(new_student)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Student enrolled successfully!'})

# --- STUDENT INTERFACE ---
@app.route('/attendance')
def take_attendance():
    return render_template('take_attendance.html')

@app.route('/api/mark_attendance', methods=['POST'])
def api_mark_attendance():
    data = request.json
    image_data = data.get('image')
    subject = data.get('subject', 'General')
    
    rgb_frame = base64_to_rgb_frame(image_data)
    
    face_locations = face_recognition.face_locations(rgb_frame)
    if not face_locations:
        return jsonify({'error': 'No face found.'}), 400
        
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
    
    students = Student.query.all()
    if not students:
        return jsonify({'error': 'No students enrolled yet.'}), 400
        
    known_encodings = [np.array(json.loads(s.face_encoding)) for s in students]
    known_students = [s for s in students]
    
    # Check the first face found in the webcam
    matches = face_recognition.compare_faces(known_encodings, face_encodings[0], tolerance=0.5)
    
    if True in matches:
        first_match_index = matches.index(True)
        student = known_students[first_match_index]
        
        today = datetime.now().date()
        now = datetime.now().time()
        
        # Time Strictness Schedule
        from datetime import time
        schedule = {
            'PECS': (time(11, 30), time(12, 30)),
            'SE': (time(12, 30), time(13, 30)),
            'AIML': (time(14, 0), time(15, 0)),
            'DAA': (time(15, 0), time(16, 0)),
            'CD': (time(16, 0), time(17, 0)),
            'CNA': (time(17, 0), time(18, 0))
        }
        
        if subject in schedule:
            start_time, end_time = schedule[subject]
            if not (start_time <= now <= end_time):
                start_str = start_time.strftime('%I:%M %p')
                end_str = end_time.strftime('%I:%M %p')
                current_str = now.strftime("%I:%M %p")
                return jsonify({'error': f'{subject} attendance can only be marked between {start_str} and {end_str}. Current time is {current_str}.'}), 400

        # Check if already marked for this specific subject today
        existing = Attendance.query.filter_by(student_id=student.id, date=today, subject=subject).first()
        if existing:
            return jsonify({'success': True, 'message': f'Attendance already marked for {student.name} (PRN: {student.prn}) in {subject}.'})
            
        new_attendance = Attendance(student_id=student.id, subject=subject)
        db.session.add(new_attendance)
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'Attendance successfully marked for {student.name} (PRN: {student.prn}) in {subject}!'})
        
    return jsonify({'error': 'Face not recognized.'}), 400

if __name__ == '__main__':
    app.run(debug=True)
