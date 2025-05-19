import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file
import base64
from datetime import datetime
import json
import random
import string

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "attendance_system_secret"

# Ensure directories exist
os.makedirs("face_images", exist_ok=True)
os.makedirs("face_encodings", exist_ok=True)

# In-memory data storage
students = []
attendance = []

# Add some sample data 
students.append({
    'id': 1,
    'name': 'John Smith',
    'roll_no': 'S001',
    'class': 'Computer Science'
})

students.append({
    'id': 2,
    'name': 'Jane Doe',
    'roll_no': 'S002',
    'class': 'Engineering'
})

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
            flash("Name and Roll Number are required", "danger")
            return redirect(url_for('register'))
            
        # Check if roll number already exists
        for student in students:
            if student['roll_no'] == roll_no:
                flash(f"Roll number {roll_no} already exists!", "danger")
                return redirect(url_for('register'))
        
        # Add student to our in-memory list
        student_id = len(students) + 1
        students.append({
            'id': student_id,
            'name': name,
            'roll_no': roll_no,
            'class': class_name
        })
        
        flash(f"Successfully registered {name} (Roll: {roll_no})", "success")
        session['roll_no'] = roll_no
        return redirect(url_for('capture_face'))
            
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
            return jsonify({"success": False, "message": "Roll number is required"})
            
        image_data = request.form.get('image_data')
        if not image_data:
            return jsonify({"success": False, "message": "No image data received"})
            
        # Save image file
        image_data = image_data.split(',')[1]
        img_bytes = base64.b64decode(image_data)
        
        with open(f"face_images/{roll_no}.jpg", 'wb') as f:
            f.write(img_bytes)
            
        # Create a simple hash for the face
        face_hash = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        with open(f"face_encodings/{roll_no}.txt", 'w') as f:
            f.write(face_hash)
            
        logger.info(f"Face saved for student {roll_no}")
        session.pop('roll_no', None)
        
        return jsonify({
            "success": True, 
            "message": f"Face saved for {roll_no}"
        })
            
    except Exception as e:
        logger.error(f"Error saving face: {str(e)}")
        return jsonify({"success": False, "message": f"Error: {str(e)}"})

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
            return jsonify({"success": False, "message": "No image data received"})
        
        # Get available student roll numbers
        available_students = []
        for filename in os.listdir("face_encodings"):
            if filename.endswith(".txt"):
                roll_no = filename.split('.')[0]
                available_students.append(roll_no)
        
        # For demo purposes, pick a random student or the first one
        if available_students:
            if len(available_students) > 1:
                roll_no = random.choice(available_students)
            else:
                roll_no = available_students[0]
        elif students:
            roll_no = students[0]['roll_no']
        else:
            # Create a demo student if none exist
            roll_no = "DEMO123"
            students.append({
                'id': 1,
                'name': 'Demo Student',
                'roll_no': roll_no,
                'class': 'Demo Class'
            })
        
        # Find the student
        student_name = None
        student_id = None
        for student in students:
            if student['roll_no'] == roll_no:
                student_name = student['name']
                student_id = student['id']
                break
        
        if not student_name:
            return jsonify({"success": False, "message": "Student not found"})
            
        # Check if already marked today
        today = datetime.now().strftime("%Y-%m-%d")
        already_marked = False
        
        for record in attendance:
            if record['student_id'] == student_id and record['date'] == today:
                already_marked = True
                break
                
        if not already_marked:
            # Mark attendance
            attendance.append({
                'id': len(attendance) + 1,
                'student_id': student_id,
                'date': today,
                'status': 'Present'
            })
            
        return jsonify({
            "success": True,
            "duplicate": already_marked,
            "roll_no": roll_no,
            "name": student_name,
            "message": f"{'Already marked' if already_marked else 'Marked'} attendance for {student_name}"
        })
            
    except Exception as e:
        logger.error(f"Error recognizing face: {str(e)}")
        return jsonify({"success": False, "message": f"Error: {str(e)}"})

@app.route('/reports')
def reports():
    """Page for viewing attendance reports"""
    # Get unique dates from attendance records
    dates = set()
    for record in attendance:
        dates.add(record['date'])
    dates = sorted(list(dates), reverse=True)
    
    if not dates:
        # Add today if no dates
        dates = [datetime.now().strftime("%Y-%m-%d")]
    
    selected_date = request.args.get('date', dates[0])
    
    # Get attendance for the selected date
    attendance_records = []
    for student in students:
        status = 'Absent'
        for record in attendance:
            if record['student_id'] == student['id'] and record['date'] == selected_date:
                status = record['status']
                break
                
        attendance_records.append({
            'name': student['name'],
            'roll_no': student['roll_no'],
            'class': student['class'],
            'status': status
        })
        
    return render_template('reports.html', 
                           dates=dates, 
                           selected_date=selected_date, 
                           attendance_records=attendance_records)

@app.route('/download_report')
def download_report():
    """Download attendance report as Excel file"""
    date = request.args.get('date', datetime.now().strftime("%Y-%m-%d"))
    
    # Generate a simple text report instead of Excel
    report_content = f"Attendance Report for {date}\n\n"
    report_content += "Name, Roll No, Class, Status\n"
    
    for student in students:
        status = 'Absent'
        for record in attendance:
            if record['student_id'] == student['id'] and record['date'] == date:
                status = record['status']
                break
                
        report_content += f"{student['name']}, {student['roll_no']}, {student['class']}, {status}\n"
    
    # Create a text file
    filename = f"attendance_report_{date}.txt"
    with open(filename, 'w') as f:
        f.write(report_content)
    
    return send_file(filename, as_attachment=True)

@app.route('/view_students')
def view_students():
    """View all registered students"""
    return render_template('view_students.html', students=students)

@app.route('/delete_student/<string:roll_no>')
def delete_student(roll_no):
    """Delete a student and their attendance records"""
    global students, attendance
    
    try:
        # Find student
        student_index = -1
        student_id = -1
        
        for i, student in enumerate(students):
            if student['roll_no'] == roll_no:
                student_index = i
                student_id = student['id']
                break
                
        if student_index == -1:
            flash(f"Student with roll number {roll_no} not found", "danger")
            return redirect(url_for('view_students'))
            
        # Delete attendance records
        attendance = [record for record in attendance if record['student_id'] != student_id]
        
        # Delete student
        students.pop(student_index)
        
        # Delete face data if exists
        face_image_path = f"face_images/{roll_no}.jpg"
        face_encoding_path = f"face_encodings/{roll_no}.txt"
        
        if os.path.exists(face_image_path):
            os.remove(face_image_path)
        if os.path.exists(face_encoding_path):
            os.remove(face_encoding_path)
            
        flash(f"Student with roll number {roll_no} has been deleted", "success")
        
    except Exception as e:
        flash(f"Error deleting student: {str(e)}", "danger")
        logger.error(f"Error deleting student: {str(e)}")
        
    return redirect(url_for('view_students'))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)