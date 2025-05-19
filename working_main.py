from flask import Flask, render_template, redirect, url_for, flash, request, session, send_file, jsonify
import os
import logging
import base64
import json
from datetime import datetime
import random
import string

# Initialize app
app = Flask(__name__)
app.secret_key = "student_attendance_system"

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure directories exist
os.makedirs("face_images", exist_ok=True)
os.makedirs("face_encodings", exist_ok=True)

# In-memory database
students = []
attendance_records = []

# Add sample students
if not students:
    students.append({
        "id": 1,
        "name": "John Smith",
        "roll_no": "S001",
        "class": "Computer Science"
    })
    students.append({
        "id": 2,
        "name": "Jane Doe",
        "roll_no": "S002",
        "class": "Engineering"
    })

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

        if not name or not roll_no:
            flash("Name and roll number are required", "danger")
            return redirect(url_for('register'))
            
        # Check if roll number exists
        for student in students:
            if student['roll_no'] == roll_no:
                flash(f"Roll number {roll_no} already exists!", "danger")
                return redirect(url_for('register'))
                
        # Add student
        student_id = len(students) + 1
        students.append({
            'id': student_id,
            'name': name,
            'roll_no': roll_no,
            'class': class_name
        })
        
        flash(f"Successfully registered {name}", "success")
        session['roll_no'] = roll_no
        return redirect(url_for('capture_face'))
            
    return render_template('register.html')

@app.route('/capture_face')
def capture_face():
    """Page to capture student's face"""
    roll_no = session.get('roll_no')
    if not roll_no:
        flash("No student selected for face capture", "danger")
        return redirect(url_for('register'))
        
    return render_template('capture_face.html', roll_no=roll_no)

@app.route('/save_face', methods=['POST'])
def save_face():
    """Save captured face image"""
    try:
        roll_no = request.form.get('roll_no')
        image_data = request.form.get('image_data')
        
        if not roll_no or not image_data:
            return jsonify({"success": False, "message": "Missing data"})
            
        # Save face image
        image_data = image_data.split(',')[1]  
        img_bytes = base64.b64decode(image_data)
        
        with open(f"face_images/{roll_no}.jpg", 'wb') as f:
            f.write(img_bytes)
            
        # Create a simple hash
        face_hash = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        with open(f"face_encodings/{roll_no}.txt", 'w') as f:
            f.write(face_hash)
            
        logger.info(f"Face image and hash saved for {roll_no}")
        session.pop('roll_no', None)
        
        return jsonify({
            "success": True,
            "message": f"Face saved for {roll_no}"
        })
            
    except Exception as e:
        logger.error(f"Error saving face: {str(e)}")
        return jsonify({"success": False, "message": str(e)})

@app.route('/take_attendance')
def take_attendance():
    """Page for taking attendance"""
    return render_template('take_attendance.html')

@app.route('/recognize', methods=['POST'])
def recognize():
    """Recognize a face and mark attendance"""
    try:
        image_data = request.form.get('image_data')
        if not image_data:
            return jsonify({"success": False, "message": "No image data"})
            
        # Demo: Get a random student or first from the list
        if students:
            if len(students) > 1:
                student = random.choice(students)
            else:
                student = students[0]
                
            roll_no = student['roll_no']
            student_name = student['name']
            student_id = student['id']
        else:
            # Create a demo student
            return jsonify({"success": False, "message": "No students registered"})
            
        # Check if attendance already marked today
        today = datetime.now().strftime("%Y-%m-%d")
        already_marked = False
        
        for record in attendance_records:
            if record['student_id'] == student_id and record['date'] == today:
                already_marked = True
                break
                
        if not already_marked:
            # Mark attendance
            attendance_records.append({
                'id': len(attendance_records) + 1,
                'student_id': student_id,
                'date': today,
                'status': 'Present'
            })
            
        return jsonify({
            "success": True,
            "duplicate": already_marked,
            "roll_no": roll_no,
            "name": student_name,
            "message": f"{'Attendance already marked' if already_marked else 'Marked present'} for {student_name}"
        })
            
    except Exception as e:
        logger.error(f"Error recognizing: {str(e)}")
        return jsonify({"success": False, "message": str(e)})

@app.route('/reports')
def reports():
    """Attendance reports page"""
    # Get unique dates
    dates = set()
    for record in attendance_records:
        dates.add(record['date'])
    dates = sorted(list(dates), reverse=True)
    
    if not dates:
        dates = [datetime.now().strftime("%Y-%m-%d")]
        
    selected_date = request.args.get('date', dates[0])
    
    # Get attendance for selected date
    records = []
    for student in students:
        status = 'Absent'
        for record in attendance_records:
            if record['student_id'] == student['id'] and record['date'] == selected_date:
                status = record['status']
                break
                
        records.append({
            'name': student['name'],
            'roll_no': student['roll_no'],
            'class': student['class'],
            'status': status
        })
        
    return render_template('reports.html', 
                          dates=dates,
                          selected_date=selected_date,
                          attendance_records=records)

@app.route('/view_students')
def view_students():
    """View all students"""
    return render_template('view_students.html', students=students)

@app.route('/delete_student/<string:roll_no>')
def delete_student(roll_no):
    """Delete a student and their attendance records"""
    global students, attendance_records
    
    # Find student
    student_index = -1
    student_id = None
    
    for i, student in enumerate(students):
        if student['roll_no'] == roll_no:
            student_index = i
            student_id = student['id']
            break
            
    if student_index == -1:
        flash(f"Student with roll number {roll_no} not found", "danger")
        return redirect(url_for('view_students'))
        
    # Delete attendance records
    if student_id:
        attendance_records = [r for r in attendance_records if r['student_id'] != student_id]
    
    # Delete student
    deleted_student = students.pop(student_index)
    
    # Delete face data
    face_image = f"face_images/{roll_no}.jpg"
    face_encoding = f"face_encodings/{roll_no}.txt"
    
    if os.path.exists(face_image):
        os.remove(face_image)
    if os.path.exists(face_encoding):
        os.remove(face_encoding)
        
    flash(f"Student {deleted_student['name']} has been deleted", "success")
    return redirect(url_for('view_students'))

@app.route('/download_report')
def download_report():
    """Download attendance report as text file"""
    date = request.args.get('date', datetime.now().strftime("%Y-%m-%d"))
    
    # Create a simple text report
    report = f"Attendance Report for {date}\n\n"
    report += "Name, Roll No, Class, Status\n"
    
    for student in students:
        status = 'Absent'
        for record in attendance_records:
            if record['student_id'] == student['id'] and record['date'] == date:
                status = record['status']
                break
                
        report += f"{student['name']}, {student['roll_no']}, {student['class']}, {status}\n"
    
    # Write to file
    filename = f"attendance_report_{date}.txt"
    with open(filename, 'w') as f:
        f.write(report)
    
    return send_file(filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)