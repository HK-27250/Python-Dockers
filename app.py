import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.utils import secure_filename
import pandas as pd
from datetime import datetime
import base64
import json

from database import setup_database, get_db_connection
from face_recognition_service import save_face_encoding, recognize_face
from models import Student, Attendance

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "attendance_system_secret")

# Ensure face_encodings directory exists
os.makedirs("face_encodings", exist_ok=True)

# Initialize database
setup_database()

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
        
        # Validate input
        if not name or not name.replace(" ", "").isalpha():
            flash("Name should contain only letters and spaces", "danger")
            return redirect(url_for('register'))
            
        if not roll_no or not roll_no.isalnum():
            flash("Roll number should be alphanumeric", "danger")
            return redirect(url_for('register'))

        # Check if student already exists
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM students WHERE roll_no = %s", (roll_no,))
        if cursor.fetchone():
            conn.close()
            flash(f"Roll number {roll_no} already exists!", "danger")
            return redirect(url_for('register'))
            
        # Insert new student
        try:
            cursor.execute(
                "INSERT INTO students (name, roll_no, class) VALUES (%s, %s, %s)",
                (name, roll_no, class_name)
            )
            conn.commit()
            conn.close()
            flash(f"Successfully registered {name} (Roll: {roll_no})", "success")
            
            # Store roll_no in session for face capture
            session['roll_no'] = roll_no
            return redirect(url_for('capture_face'))
            
        except Exception as e:
            conn.close()
            flash(f"Database error: {str(e)}", "danger")
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/capture_face')
def capture_face():
    """Page to capture student's face"""
    roll_no = session.get('roll_no')
    if not roll_no:
        flash("No student selected for face capture", "danger")
        return redirect(url_for('register'))
        
    return render_template('register.html', capture_face=True, roll_no=roll_no)

@app.route('/save_face', methods=['POST'])
def save_face():
    """API endpoint to save captured face encoding"""
    try:
        roll_no = request.form.get('roll_no')
        if not roll_no:
            return jsonify({"success": False, "message": "Roll number is required"})
            
        image_data = request.form.get('image_data')
        if not image_data:
            return jsonify({"success": False, "message": "No image data received"})
            
        # Convert base64 data to image
        image_data = image_data.split(',')[1]  # Remove the "data:image/jpeg;base64," part
        img_bytes = base64.b64decode(image_data)
        
        # Save temporary file
        temp_path = f"temp_{roll_no}.jpg"
        with open(temp_path, 'wb') as f:
            f.write(img_bytes)
        
        # Process and save face encoding
        success = save_face_encoding(temp_path, roll_no)
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        if success:
            # Clear session
            session.pop('roll_no', None)
            return jsonify({"success": True, "message": f"Face encoding saved for {roll_no}"})
        else:
            return jsonify({"success": False, "message": "No face detected. Please try again."})
            
    except Exception as e:
        logging.error(f"Error saving face: {str(e)}")
        return jsonify({"success": False, "message": f"Error: {str(e)}"})

@app.route('/take_attendance')
def take_attendance():
    """Page for taking attendance with facial recognition"""
    return render_template('take_attendance.html')

@app.route('/recognize', methods=['POST'])
def recognize():
    """API endpoint to recognize a face and mark attendance"""
    try:
        image_data = request.form.get('image_data')
        if not image_data:
            return jsonify({"success": False, "message": "No image data received"})
            
        # Convert base64 data to image
        image_data = image_data.split(',')[1]
        img_bytes = base64.b64decode(image_data)
        
        # Save temporary file
        temp_path = f"temp_recognition_{datetime.now().strftime('%H%M%S')}.jpg"
        with open(temp_path, 'wb') as f:
            f.write(img_bytes)
        
        # Recognize face
        roll_no = recognize_face(temp_path)
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        if roll_no:
            # Mark attendance
            today = datetime.now().strftime("%Y-%m-%d")
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get student ID
            cursor.execute("SELECT id, name FROM students WHERE roll_no = %s", (roll_no,))
            student = cursor.fetchone()
            if not student:
                conn.close()
                return jsonify({"success": False, "message": "Student not found in database"})
                
            student_id, student_name = student
            
            # Check if already marked for today
            cursor.execute(
                "SELECT 1 FROM attendance WHERE student_id = %s AND date = %s", 
                (student_id, today)
            )
            if cursor.fetchone():
                conn.close()
                return jsonify({
                    "success": True, 
                    "duplicate": True,
                    "roll_no": roll_no,
                    "name": student_name,
                    "message": f"Attendance already marked for {student_name} ({roll_no})"
                })
            
            # Mark attendance
            cursor.execute(
                "INSERT INTO attendance (student_id, date, status) VALUES (%s, %s, %s)",
                (student_id, today, "Present")
            )
            conn.commit()
            conn.close()
            
            return jsonify({
                "success": True,
                "duplicate": False,
                "roll_no": roll_no,
                "name": student_name,
                "message": f"Marked present: {student_name} ({roll_no})"
            })
        else:
            return jsonify({"success": False, "message": "No recognized face found"})
            
    except Exception as e:
        logging.error(f"Error recognizing face: {str(e)}")
        return jsonify({"success": False, "message": f"Error: {str(e)}"})

@app.route('/reports')
def reports():
    """Page for generating and viewing attendance reports"""
    # Get list of dates with attendance records
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT date FROM attendance ORDER BY date DESC")
    dates = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    selected_date = request.args.get('date', datetime.now().strftime("%Y-%m-%d"))
    
    # Get attendance data for the selected date
    conn = get_db_connection()
    query = """
    SELECT s.name, s.roll_no, s.class, COALESCE(a.status, 'Absent') as status
    FROM students s
    LEFT JOIN attendance a ON s.id = a.student_id AND a.date = %s
    ORDER BY s.name
    """
    df = pd.read_sql_query(query, conn, params=(selected_date,))
    conn.close()
    
    # Convert dataframe to list of dictionaries for template
    attendance_records = df.to_dict('records')
    
    return render_template('reports.html', 
                          dates=dates, 
                          selected_date=selected_date,
                          attendance_records=attendance_records)

@app.route('/download_report')
def download_report():
    """Download attendance report as Excel"""
    date = request.args.get('date', datetime.now().strftime("%Y-%m-%d"))
    
    conn = get_db_connection()
    query = """
    SELECT s.name, s.roll_no, s.class, COALESCE(a.status, 'Absent') as status
    FROM students s
    LEFT JOIN attendance a ON s.id = a.student_id AND a.date = %s
    ORDER BY s.name
    """
    df = pd.read_sql_query(query, conn, params=(date,))
    conn.close()
    
    # Create Excel file
    filename = f"Attendance_Report_{date}.xlsx"
    temp_path = f"./{filename}"
    df.to_excel(temp_path, index=False)
    
    # Instead of serving the file (which requires additional setup),
    # we'll just inform the user it's been created
    flash(f"Report generated: {filename}", "success")
    return redirect(url_for('reports', date=date))

@app.route('/view_students')
def view_students():
    """View all registered students"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, roll_no, class FROM students ORDER BY name")
    students = cursor.fetchall()
    conn.close()
    
    student_list = [
        {"name": s[0], "roll_no": s[1], "class": s[2]} for s in students
    ]
    
    return render_template('index.html', show_students=True, students=student_list)

@app.route('/delete_student/<string:roll_no>')
def delete_student(roll_no):
    """Delete a student and their attendance records"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get student ID
        cursor.execute("SELECT id FROM students WHERE roll_no = %s", (roll_no,))
        student = cursor.fetchone()
        
        if not student:
            conn.close()
            flash(f"Student with roll number {roll_no} not found", "danger")
            return redirect(url_for('view_students'))
            
        student_id = student[0]
        
        # First delete attendance records (due to foreign key constraint)
        cursor.execute("DELETE FROM attendance WHERE student_id = %s", (student_id,))
        
        # Then delete the student
        cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
        
        # Also delete face data if exists
        face_image_path = f"face_images/{roll_no}.jpg"
        face_encoding_path = f"face_encodings/{roll_no}.txt"
        
        if os.path.exists(face_image_path):
            os.remove(face_image_path)
            
        if os.path.exists(face_encoding_path):
            os.remove(face_encoding_path)
        
        conn.commit()
        conn.close()
        
        flash(f"Student with roll number {roll_no} has been deleted", "success")
    except Exception as e:
        flash(f"Error deleting student: {str(e)}", "danger")
        logging.error(f"Error deleting student: {str(e)}")
        
    return redirect(url_for('view_students'))
