import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename
import pandas as pd
from datetime import datetime
import base64
import json

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# Import models and services
from face_recognition_service import save_face_encoding, recognize_face

# Ensure directories exist
os.makedirs("face_encodings", exist_ok=True)
os.makedirs("face_images", exist_ok=True)

# Define models
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    roll_no = db.Column(db.String(50), unique=True, nullable=False)
    class_name = db.Column(db.String(50), name='class')
    
    # Relationship with attendance
    attendance_records = db.relationship('Attendance', backref='student', lazy=True, cascade='all, delete-orphan')

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    date = db.Column(db.String(10), nullable=False)  # YYYY-MM-DD format
    status = db.Column(db.String(20), nullable=False, default='Present')

# Create tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    """Home page with menu options"""
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Student registration page"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        roll_no = request.form.get('roll_no', '').strip()
        class_name = request.form.get('class_name', '').strip()

        if not name or not name.replace(" ", "").isalpha():
            flash("Name should contain only letters and spaces", "danger")
            return redirect(url_for('register'))

        if not roll_no or not roll_no.isalnum():
            flash("Roll number should be alphanumeric", "danger")
            return redirect(url_for('register'))

        # Check if roll number already exists
        existing_student = Student.query.filter_by(roll_no=roll_no).first()
        if existing_student:
            flash(f"Roll number {roll_no} already exists!", "danger")
            return redirect(url_for('register'))

        try:
            # Create new student
            student = Student(name=name, roll_no=roll_no, class_name=class_name)
            db.session.add(student)
            db.session.commit()
            
            flash(f"Successfully registered {name} (Roll: {roll_no})", "success")
            session['roll_no'] = roll_no
            return redirect(url_for('capture_face'))
        except Exception as e:
            db.session.rollback()
            flash(f"Database error: {str(e)}", "danger")
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/capture_face')
def capture_face():
    """Capture student's face"""
    roll_no = session.get('roll_no')
    if not roll_no:
        flash("No student selected for face capture", "danger")
        return redirect(url_for('register'))

    return render_template('capture_face.html', roll_no=roll_no)

@app.route('/save_face', methods=['POST'])
def save_face():
    """Save captured face encoding"""
    try:
        roll_no = request.form.get('roll_no')
        if not roll_no:
            return jsonify({
                "success": False,
                "message": "Roll number is required"
            })

        image_data = request.form.get('image_data')
        if not image_data:
            return jsonify({
                "success": False,
                "message": "No image data received"
            })

        image_data = image_data.split(',')[1]
        img_bytes = base64.b64decode(image_data)

        temp_path = f"temp_{roll_no}.jpg"
        with open(temp_path, 'wb') as f:
            f.write(img_bytes)

        success = save_face_encoding(temp_path, roll_no)

        if os.path.exists(temp_path):
            os.remove(temp_path)

        if success:
            session.pop('roll_no', None)
            return jsonify({
                "success": True,
                "message": f"Face encoding saved for {roll_no}"
            })
        else:
            return jsonify({
                "success": False,
                "message": "No face detected. Please try again."
            })

    except Exception as e:
        logging.error(f"Error saving face: {str(e)}")
        return jsonify({"success": False, "message": f"Error: {str(e)}"})

@app.route('/take_attendance')
def take_attendance():
    return render_template('take_attendance.html')

@app.route('/recognize', methods=['POST'])
def recognize():
    try:
        image_data = request.form.get('image_data')
        if not image_data:
            return jsonify({
                "success": False,
                "message": "No image data received"
            })

        image_data = image_data.split(',')[1]
        img_bytes = base64.b64decode(image_data)

        temp_path = f"temp_recognition_{datetime.now().strftime('%H%M%S')}.jpg"
        with open(temp_path, 'wb') as f:
            f.write(img_bytes)

        roll_no = recognize_face(temp_path)

        if os.path.exists(temp_path):
            os.remove(temp_path)

        if roll_no:
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Find the student
            student = Student.query.filter_by(roll_no=roll_no).first()
            if not student:
                return jsonify({
                    "success": False,
                    "message": "Student not found in database"
                })

            # Check if attendance already marked
            existing_attendance = Attendance.query.filter_by(
                student_id=student.id, 
                date=today
            ).first()
            
            if existing_attendance:
                return jsonify({
                    "success": True,
                    "duplicate": True,
                    "roll_no": roll_no,
                    "name": student.name,
                    "message": f"Attendance already marked for {student.name} ({roll_no})"
                })

            # Mark attendance
            attendance = Attendance(student_id=student.id, date=today, status="Present")
            db.session.add(attendance)
            db.session.commit()

            return jsonify({
                "success": True,
                "duplicate": False,
                "roll_no": roll_no,
                "name": student.name,
                "message": f"Marked present: {student.name} ({roll_no})"
            })
        else:
            return jsonify({
                "success": False,
                "message": "No recognized face found"
            })

    except Exception as e:
        logging.error(f"Error recognizing face: {str(e)}")
        return jsonify({"success": False, "message": f"Error: {str(e)}"})

@app.route('/reports')
def reports():
    # Get all unique dates from attendance records
    dates_query = db.session.query(Attendance.date).distinct().order_by(Attendance.date.desc())
    dates = [date[0] for date in dates_query.all()]
    
    selected_date = request.args.get('date', datetime.now().strftime("%Y-%m-%d"))
    
    # Get attendance records for the selected date
    query = db.session.query(
        Student.name,
        Student.roll_no,
        Student.class_name,
        db.func.coalesce(Attendance.status, 'Absent').label('status')
    ).outerjoin(
        Attendance, 
        db.and_(Student.id == Attendance.student_id, Attendance.date == selected_date)
    ).order_by(Student.name)
    
    attendance_records = query.all()
    
    # Convert to dictionary format
    records = [{
        'name': record.name,
        'roll_no': record.roll_no,
        'class': record.class_name,
        'status': record.status
    } for record in attendance_records]
    
    return render_template('reports.html',
                         dates=dates,
                         selected_date=selected_date,
                         attendance_records=records)

@app.route('/download_report')
def download_report():
    date = request.args.get('date', datetime.now().strftime("%Y-%m-%d"))
    
    # Get attendance records for the selected date
    query = db.session.query(
        Student.name,
        Student.roll_no,
        Student.class_name,
        db.func.coalesce(Attendance.status, 'Absent').label('status')
    ).outerjoin(
        Attendance, 
        db.and_(Student.id == Attendance.student_id, Attendance.date == date)
    ).order_by(Student.name)
    
    attendance_records = query.all()
    
    # Convert to pandas DataFrame
    data = [{
        'Name': record.name,
        'Roll Number': record.roll_no,
        'Class': record.class_name,
        'Status': record.status
    } for record in attendance_records]
    
    df = pd.DataFrame(data)
    
    filename = f"Attendance_Report_{date}.xlsx"
    df.to_excel(filename, index=False)
    
    return send_file(filename, as_attachment=True)

@app.route('/view_students')
def view_students():
    students = Student.query.order_by(Student.name).all()
    
    student_list = [{
        "name": s.name,
        "roll_no": s.roll_no,
        "class": s.class_name
    } for s in students]
    
    return render_template('view_students.html', students=student_list)

@app.route('/delete_student/<string:roll_no>')
def delete_student(roll_no):
    try:
        student = Student.query.filter_by(roll_no=roll_no).first()
        
        if not student:
            flash(f"Student with roll number {roll_no} not found", "danger")
            return redirect(url_for('view_students'))

        # Delete associated files
        face_image_path = f"face_images/{roll_no}.jpg"
        face_encoding_path = f"face_encodings/{roll_no}.txt"

        if os.path.exists(face_image_path):
            os.remove(face_image_path)
        if os.path.exists(face_encoding_path):
            os.remove(face_encoding_path)

        # Delete student (attendance records will be cascade deleted)
        db.session.delete(student)
        db.session.commit()
        
        flash(f"Student with roll number {roll_no} has been deleted", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting student: {str(e)}", "danger")
        logging.error(f"Error deleting student: {str(e)}")

    return redirect(url_for('view_students'))

if __name__ == "__main__":
    app.run(debug=True)