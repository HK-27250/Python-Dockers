import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file
import base64
from datetime import datetime

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "attendance_system_secret")

# Ensure directories exist
os.makedirs("face_images", exist_ok=True)
os.makedirs("face_encodings", exist_ok=True)

# In-memory storage for demonstration
students = []
attendance_records = []

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

        # Simple validation
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
    """Save captured face"""
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
        
        os.makedirs("face_images", exist_ok=True)
        with open(f"face_images/{roll_no}.jpg", 'wb') as f:
            f.write(img_bytes)
            
        # Create a simple hash for the face
        os.makedirs("face_encodings", exist_ok=True)
        with open(f"face_encodings/{roll_no}.txt", 'w') as f:
            f.write(f"face_hash_{roll_no}")
            
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
            
        # For demo, just return the first student or a default one
        if students:
            roll_no = students[0]['roll_no']
            student_name = students[0]['name']
            student_id = students[0]['id']
        else:
            # Create a demo student if none exist
            roll_no = "DEMO123"
            student_name = "Demo Student"
            student_id = 1
            
        # Check if already marked today
        today = datetime.now().strftime("%Y-%m-%d")
        
        for record in attendance_records:
            if record['student_id'] == student_id and record['date'] == today:
                return jsonify({
                    "success": True,
                    "duplicate": True,
                    "roll_no": roll_no,
                    "name": student_name,
                    "message": f"Attendance already marked for {student_name} ({roll_no})"
                })
                
        # Mark attendance
        attendance_records.append({
            'id': len(attendance_records) + 1,
            'student_id': student_id,
            'date': today,
            'status': 'Present'
        })
        
        logger.info(f"Marked attendance for {student_name} ({roll_no})")
        
        return jsonify({
            "success": True,
            "duplicate": False,
            "roll_no": roll_no,
            "name": student_name,
            "message": f"Marked present: {student_name} ({roll_no})"
        })
            
    except Exception as e:
        logger.error(f"Error recognizing face: {str(e)}")
        return jsonify({"success": False, "message": f"Error: {str(e)}"})

@app.route('/reports')
def reports():
    """Page for viewing attendance reports"""
    # Get unique dates from attendance records
    dates = set()
    for record in attendance_records:
        dates.add(record['date'])
    dates = sorted(list(dates), reverse=True)
    
    selected_date = request.args.get('date', datetime.now().strftime("%Y-%m-%d"))
    
    # Get attendance for the selected date
    attendance_for_date = []
    for student in students:
        status = 'Absent'
        for record in attendance_records:
            if record['student_id'] == student['id'] and record['date'] == selected_date:
                status = record['status']
                break
                
        attendance_for_date.append({
            'name': student['name'],
            'roll_no': student['roll_no'],
            'class': student['class'],
            'status': status
        })
        
    return render_template('reports.html', 
                           dates=dates, 
                           selected_date=selected_date, 
                           attendance_records=attendance_for_date)

@app.route('/view_students')
def view_students():
    """View all registered students"""
    return render_template('view_students.html', students=students)

@app.route('/delete_student/<string:roll_no>')
def delete_student(roll_no):
    """Delete a student and their attendance records"""
    global students, attendance_records
    
    try:
        # Find student
        student_to_delete = None
        student_index = -1
        for i, student in enumerate(students):
            if student['roll_no'] == roll_no:
                student_to_delete = student
                student_index = i
                break
                
        if student_index == -1:
            flash(f"Student with roll number {roll_no} not found", "danger")
            return redirect(url_for('view_students'))
            
        # Delete attendance records
        attendance_records = [record for record in attendance_records 
                              if record['student_id'] != student_to_delete['id']]
        
        # Delete student
        if student_index >= 0:
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