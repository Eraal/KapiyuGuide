from app.models import Inquiry, InquiryMessage, User, Office, db, OfficeAdmin, Student, CounselingSession, StudentActivityLog, SuperAdminActivityLog, OfficeLoginLog, AuditLog
from flask import Blueprint, redirect, url_for, render_template, jsonify, request, flash, Response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, current_user
from flask_socketio import emit
from app import socketio
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from sqlalchemy import func, case, or_
import random
import os
from app.admin import admin_bp



################################ PROFILE MANAGEMENT ###################################################################

@admin_bp.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    if not current_user.role == 'office_admin' and not current_user.role == 'super_admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        # Get form data
        first_name = request.form.get('first_name')
        middle_name = request.form.get('middle_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        
        # Validate required fields
        if not first_name or not last_name or not email:
            flash('Please fill all required fields', 'error')
            return redirect(url_for('admin.dashboard'))
        
        # Check if email is already in use (if changed)
        if email != current_user.email:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('Email address is already in use', 'error')
                return redirect(url_for('admin.dashboard'))
        
        # Update user data
        current_user.first_name = first_name
        current_user.middle_name = middle_name
        current_user.last_name = last_name
        current_user.email = email
        
        db.session.commit()
        flash('Profile updated successfully', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating profile: {str(e)}', 'error')
    
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/update_profile_photo', methods=['POST'])
@login_required
def update_profile_photo():
    if not current_user.role == 'office_admin' and not current_user.role == 'super_admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        if 'profile_photo' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(url_for('admin.dashboard'))
        
        file = request.files['profile_photo']
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('admin.dashboard'))
        
        if file:
            # Define allowed file extensions
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
            if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
                flash('Invalid file format. Please upload a JPG, PNG, or GIF file.', 'error')
                return redirect(url_for('admin.dashboard'))
            
            # Create upload directory if it doesn't exist
            upload_dir = os.path.join('app', 'static', 'uploads', 'profile_pics')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Create unique filename
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"user_{current_user.id}_{timestamp}_{secure_filename(file.filename)}"
            filepath = os.path.join(upload_dir, filename)
            
            # Save the file
            file.save(filepath)
            

            db_filepath = os.path.join('uploads', 'profile_pics', filename)
            
            # Delete old profile pic if exists
            if current_user.profile_pic:
                old_file_path = os.path.join('app', 'static', current_user.profile_pic)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
            
            current_user.profile_pic = db_filepath
            db.session.commit()
            
            flash('Profile photo updated successfully', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating profile photo: {str(e)}', 'error')
    
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/remove_profile_photo', methods=['POST'])
@login_required
def remove_profile_photo():
    if not current_user.role == 'office_admin' and not current_user.role == 'super_admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        if current_user.profile_pic:
            file_path = os.path.join('app', 'static', current_user.profile_pic)
            if os.path.exists(file_path):
                os.remove(file_path)
            
            current_user.profile_pic = None
            db.session.commit()
            
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'No profile photo to remove'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@admin_bp.route('/change_password', methods=['POST'])
@login_required
def change_password():
    if not current_user.role == 'office_admin' and not current_user.role == 'super_admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_new_password = request.form.get('confirm_new_password')
        
        # Validate passwords
        if not current_password or not new_password or not confirm_new_password:
            flash('All password fields are required', 'error')
            return redirect(url_for('admin.dashboard'))
        
        if new_password != confirm_new_password:
            flash('New passwords do not match', 'error')
            return redirect(url_for('admin.dashboard'))
        
        # Verify current password
        if not check_password_hash(current_user.password_hash, current_password):
            flash('Current password is incorrect', 'error')
            return redirect(url_for('admin.dashboard'))
        
        # Update password
        current_user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
        flash('Password changed successfully', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error changing password: {str(e)}', 'error')
    
    return redirect(url_for('admin.dashboard'))
