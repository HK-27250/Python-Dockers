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
    
    This implementation compares image hashes to find the best match
    
    Args:
        image_path: Path to the image file to check
        
    Returns:
        str: Roll number of the matched student, or None if no match
    """
    try:
        # Get list of all registered students
        encoding_dir = "face_encodings"
        images_dir = "face_images"
        
        if not os.path.exists(encoding_dir) or not os.path.exists(images_dir):
            logging.warning("Face encodings or images directory not found")
            return None
            
        # Get all student encodings
        students = [f.split(".")[0] for f in os.listdir(encoding_dir) if f.endswith(".txt")]
        
        if not students:
            logging.warning("No students found in the database")
            return None
        
        # Get hash of the captured image
        with open(image_path, 'rb') as f:
            captured_hash = hashlib.md5(f.read()).hexdigest()
        
        # Compare with all saved hashes to find best match
        best_match = None
        best_similarity = 0
        
        for student_id in students:
            # Read the stored hash
            hash_path = os.path.join(encoding_dir, f"{student_id}.txt")
            if not os.path.exists(hash_path):
                continue
                
            with open(hash_path, 'r') as f:
                stored_hash = f.read().strip()
            
            # Calculate similarity (number of matching characters in hash)
            similarity = sum(c1 == c2 for c1, c2 in zip(captured_hash, stored_hash))
            similarity_percent = (similarity / len(captured_hash)) * 100
            
            logging.info(f"Student {student_id} similarity: {similarity_percent:.2f}%")
            
            # Update best match if better similarity found
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = student_id
        
        # We'll set a minimum threshold for similarity
        if best_similarity > (len(captured_hash) * 0.5):  # At least 50% similarity
            logging.info(f"Recognition match: {best_match} with {best_similarity / len(captured_hash) * 100:.2f}% similarity")
            return best_match
        else:
            logging.warning(f"No good match found. Best was {best_match} with only {best_similarity / len(captured_hash) * 100:.2f}% similarity")
            return None
            
    except Exception as e:
        logging.error(f"Error in face recognition: {str(e)}")
        return None
