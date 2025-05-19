from flask import Flask, render_template, redirect, url_for, flash, request
import os
import json

app = Flask(__name__)
app.secret_key = "student_management_secret"

# Create a data folder if it doesn't exist
os.makedirs("data", exist_ok=True)

# Path to our student data file
STUDENT_DATA_FILE = "data/students.json"

# Initialize with sample students if the file doesn't exist
if not os.path.exists(STUDENT_DATA_FILE):
    sample_students = [
        {"id": 1, "name": "John Doe", "roll_no": "S001", "class": "Computer Science"},
        {"id": 2, "name": "Jane Smith", "roll_no": "S002", "class": "Engineering"},
        {"id": 3, "name": "Bob Johnson", "roll_no": "S003", "class": "Mathematics"}
    ]
    with open(STUDENT_DATA_FILE, 'w') as f:
        json.dump(sample_students, f)

def get_students():
    """Get the current list of students"""
    if os.path.exists(STUDENT_DATA_FILE):
        with open(STUDENT_DATA_FILE, 'r') as f:
            return json.load(f)
    return []

def save_students(students):
    """Save the students list to the file"""
    with open(STUDENT_DATA_FILE, 'w') as f:
        json.dump(students, f)

@app.route('/')
def home():
    """Home page displaying all students"""
    students = get_students()
    return render_template('students.html', students=students)

@app.route('/delete/<roll_no>')
def delete_student(roll_no):
    """Delete a student by roll number"""
    students = get_students()
    
    # Find student by roll number
    student_index = -1
    for i, student in enumerate(students):
        if student['roll_no'] == roll_no:
            student_index = i
            break
    
    if student_index != -1:
        # Delete the student
        removed_student = students.pop(student_index)
        save_students(students)
        flash(f"Student {removed_student['name']} with roll number {roll_no} has been deleted", "success")
    else:
        flash(f"Student with roll number {roll_no} not found", "danger")
    
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)