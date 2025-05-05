# Models for the attendance system (these are just type definitions for documentation)
class Student:
    """Student model structure (maps to students table)"""
    id: int
    name: str
    roll_no: str
    class_name: str
    
class Attendance:
    """Attendance model structure (maps to attendance table)"""
    id: int
    student_id: int
    date: str  # YYYY-MM-DD format
    status: str  # "Present" or other statuses
