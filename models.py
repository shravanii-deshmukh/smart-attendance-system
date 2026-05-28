from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class Teacher(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prn = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    # Storing the face encoding as a JSON string
    face_encoding = db.Column(db.Text, nullable=False)

def get_current_date():
    return datetime.now().date()

def get_current_time():
    return datetime.now().time()

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=get_current_date)
    time = db.Column(db.Time, nullable=False, default=get_current_time)
    subject = db.Column(db.String(100), nullable=False, default='General')
    status = db.Column(db.String(20), nullable=False, default='Present')
    
    # Relationship to fetch student details easily
    student = db.relationship('Student', backref=db.backref('attendances', lazy=True))
