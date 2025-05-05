import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

def save_profile_picture(file):
    """
    Save a profile picture to the uploads directory
    
    Args:
        file: The file object from the form
        
    Returns:
        str: The filename that was saved
    """
    # Create a unique filename to prevent overwriting
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    
    # Create directory if it doesn't exist
    upload_folder = os.path.join(current_app.static_folder, 'uploads', 'profile_pics')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    # Save the file
    file_path = os.path.join(upload_folder, unique_filename)
    file.save(file_path)
    
    return unique_filename

def delete_profile_picture(filename):
    """
    Delete a profile picture from the uploads directory
    
    Args:
        filename: The filename to delete
    """
    if not filename:
        return
    
    file_path = os.path.join(current_app.static_folder, 'uploads', 'profile_pics', filename)
    if os.path.exists(file_path):
        os.remove(file_path)