import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import base64
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "attendance_system_secret")

# Ensure directories exist
os.makedirs("face_images", exist_ok=True)
os.makedirs("face_encodings", exist_ok=True)

# For demo, use simple in-memory storage
students = []
attendance = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        roll_no = request.form.get('roll_no')
        class_name = request.form.get('class_name')
        
        # Check if roll_no already exists
        for student in students:
            if student['roll_no'] == roll_no:
                flash("Roll number already exists!", "danger")
                return redirect(url_for('register'))
                
        # Add new student
        student_id = len(students) + 1
        students.append({
            'id': student_id,
            'name': name,
            'roll_no': roll_no,
            'class': class_name
        })
        
        flash(f"Student {name} registered successfully!", "success")
        session['roll_no'] = roll_no
        return redirect(url_for('capture_face'))
        
    return render_template('register.html')

@app.route('/capture_face')
def capture_face():
    roll_no = session.get('roll_no')
    if not roll_no:
        flash("No student selected for face capture", "danger")
        return redirect(url_for('register'))
        
    return render_template('capture_face.html', roll_no=roll_no)

@app.route('/save_face', methods=['POST'])
def save_face():
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
            
        # Save a simple face hash
        with open(f"face_encodings/{roll_no}.txt", 'w') as f:
            f.write(f"demo_hash_{roll_no}")
            
        session.pop('roll_no', None)
        return jsonify({"success": True, "message": "Face saved successfully"})
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/take_attendance')
def take_attendance():
    return render_template('take_attendance.html')

@app.route('/recognize', methods=['POST'])
def recognize():
    try:
        image_data = request.form.get('image_data')
        if not image_data:
            return jsonify({"success": False, "message": "No image data"})
            
        # For demo purposes, just recognize the first student
        # Or select one from the available face encodings
        face_files = []
        if os.path.exists("face_encodings"):
            face_files = [f.split('.')[0] for f in os.listdir("face_encodings") if f.endswith('.txt')]
            
        roll_no = face_files[0] if face_files else "DEMO123"
        
        # Find student info
        student_name = "Demo Student"
        student_id = 1
        
        for student in students:
            if student['roll_no'] == roll_no:
                student_name = student['name']
                student_id = student['id']
                break
                
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
        return jsonify({"success": False, "message": str(e)})

@app.route('/reports')
def reports():
    # Get unique dates
    dates = set()
    for record in attendance:
        dates.add(record['date'])
    
    dates = sorted(list(dates), reverse=True)
    
    selected_date = request.args.get('date', datetime.now().strftime("%Y-%m-%d"))
    
    # Get attendance for selected date
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

@app.route('/view_students')
def view_students():
    return render_template('view_students.html', students=students)

@app.route('/delete_student/<string:roll_no>')
def delete_student(roll_no):
    global students, attendance
    
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
    
    # Delete face data
    face_image = f"face_images/{roll_no}.jpg"
    face_encoding = f"face_encodings/{roll_no}.txt"
    
    if os.path.exists(face_image):
        os.remove(face_image)
    if os.path.exists(face_encoding):
        os.remove(face_encoding)
        
    flash(f"Student with roll number {roll_no} has been deleted", "success")
    return redirect(url_for('view_students'))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)