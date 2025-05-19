from flask import Flask, render_template, request, redirect, url_for, flash
import os

app = Flask(__name__)
app.secret_key = "secret_key"

# Sample student data
students = [
    {"id": 1, "name": "John Doe", "roll_no": "S001", "class": "Computer Science"},
    {"id": 2, "name": "Jane Smith", "roll_no": "S002", "class": "Engineering"},
    {"id": 3, "name": "Bob Johnson", "roll_no": "S003", "class": "Mathematics"}
]

@app.route('/')
def home():
    return render_template('students.html', students=students)

@app.route('/delete/<roll_no>')
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
        
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)