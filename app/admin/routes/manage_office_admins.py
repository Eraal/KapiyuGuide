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

################################# ADMIN ACCOUNT SETTINGS ###############################################

@admin_bp.route('/manage-office-admins', methods=['GET', 'POST'])
@login_required
def manage_office_admins():
    if current_user.role != 'super_admin':
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        office_id = request.form.get('office_id')
        
        # Validate inputs
        if not first_name or not last_name or not email or not password or not office_id:
            flash('All fields are required.', 'error')
            offices = Office.query.all()
            return render_template('admin/manage_office_admins.html', offices=offices)
        
        # Check if user with this email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('A user with this email already exists.', 'error')
            offices = Office.query.all()
            return render_template('admin/manage_office_admins.html', offices=offices)
        
        # Create new user - setting is_active to False until first login
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=generate_password_hash(password),
            role='office_admin',
            is_active=False  # Changed from True to False
        )
        
        db.session.add(new_user)
        db.session.flush()  # To get the new user ID
        
        # Create office admin association
        new_admin = OfficeAdmin(user_id=new_user.id, office_id=office_id)
        db.session.add(new_admin)
        
        # Log activity
        log = SuperAdminActivityLog(
            super_admin_id=current_user.id,
            action=f"Created new office admin: {first_name} {last_name} for office ID: {office_id}",
            timestamp=datetime.utcnow()
        )
        db.session.add(log)
        
        try:
            db.session.commit()
            flash('New admin created and assigned to office successfully! Account will be activated upon first login.', 'success')
            return redirect(url_for('admin.office_stats'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while creating the admin: {str(e)}', 'error')
    
    offices = Office.query.all()
    return render_template('admin/manage_office_admins.html', offices=offices)
