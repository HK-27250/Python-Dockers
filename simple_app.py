from flask import Flask, render_template, flash, redirect, url_for
import os

app = Flask(__name__)
app.secret_key = "attendance_system_secret"

# Sample student data
students = [
    {"id": 1, "name": "John Doe", "roll_no": "S001", "class": "Computer Science"},
    {"id": 2, "name": "Jane Smith", "roll_no": "S002", "class": "Engineering"}
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/view_students')
def view_students():
    return render_template('view_students.html', students=students)

@app.route('/delete_student/<string:roll_no>')
def delete_student(roll_no):
    global students
    
    # Find student index
    student_index = -1
    for i, student in enumerate(students):
        if student['roll_no'] == roll_no:
            student_index = i
            break
            
    if student_index != -1:
        # Delete student
        removed_student = students.pop(student_index)
        flash(f"Student {removed_student['name']} with roll number {roll_no} has been deleted", "success")
    else:
        flash(f"Student with roll number {roll_no} not found", "danger")
        
    return redirect(url_for('view_students'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)