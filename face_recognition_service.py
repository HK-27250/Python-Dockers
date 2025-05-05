import os
import logging
import hashlib
import base64
from datetime import datetime

# Initialize logging
logging.basicConfig(level=logging.DEBUG)

def save_face_encoding(image_path, roll_no):
    """
    Process an image and save it for the student
    
    This is a simplified version that just saves the image file
    and creates a simple hash instead of using actual face recognition
    
    Args:
        image_path: Path to the temporary image file
        roll_no: Student's roll number to use as filename
        
    Returns:
        bool: True if image was saved, False otherwise
    """
    try:
        # Ensure directory exists
        os.makedirs("face_images", exist_ok=True)
        
        # We're bypassing actual face detection here for simplicity
        # In a real application, you would use face recognition libraries
        
        # Create a copy of the image
        save_path = f"face_images/{roll_no}.jpg"
        with open(image_path, 'rb') as src, open(save_path, 'wb') as dst:
            dst.write(src.read())
        
        # Create a simple hash from the image data and save it
        with open(save_path, 'rb') as f:
            image_hash = hashlib.md5(f.read()).hexdigest()
        
        os.makedirs("face_encodings", exist_ok=True)
        with open(f"face_encodings/{roll_no}.txt", 'w') as f:
            f.write(image_hash)
            
        logging.info(f"Face image and hash saved for {roll_no}")
        return True
            
    except Exception as e:
        logging.error(f"Error saving face: {str(e)}")
        return False

def recognize_face(image_path):
    """
    Recognize a face in an image by comparing with saved images
    
    This is a simplified version that returns the most recently
    added student without actual face recognition
    
    Args:
        image_path: Path to the image file to check
        
    Returns:
        str: Roll number of the matched student, or None if no match
    """
    try:
        # Get list of all registered students
        encoding_dir = "face_encodings"
        if not os.path.exists(encoding_dir):
            logging.warning("No face encodings directory found")
            return None
            
        # In a real application, you would do actual face recognition
        # For demo purposes, we'll just return a student from our database
        
        # Get the most recently created file based on modification time
        files = [(f, os.path.getmtime(os.path.join(encoding_dir, f))) 
                 for f in os.listdir(encoding_dir) if f.endswith(".txt")]
        
        if not files:
            logging.warning("No students found in the database")
            return None
            
        # Sort by modification time (newest first)
        files.sort(key=lambda x: x[1], reverse=True)
        
        # Get roll number from the filename
        roll_no = files[0][0].split(".")[0]
        logging.info(f"Simulating recognition: returned {roll_no}")
        return roll_no
            
    except Exception as e:
        logging.error(f"Error in face recognition: {str(e)}")
        return None
