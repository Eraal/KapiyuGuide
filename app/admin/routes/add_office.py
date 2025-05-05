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

# Add Office
@admin_bp.route('/add-office', methods=['GET', 'POST'])
@login_required
def add_office():
    if current_user.role != 'super_admin':
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        supports_video = request.form.get('supports_video', False)

        
        # Check if office with same name already exists
        existing_office = Office.query.filter_by(name=name).first()
        if existing_office:
            flash('An office with this name already exists.', 'error')
            return render_template('admin/add_office.html')
        
        new_office = Office(
            name=name,
            description=description,
            supports_video=supports_video == 'true'
        )
        
        # Log activity
        log = SuperAdminActivityLog(
            super_admin_id=current_user.id,
            action=f"Created new office: {name}",
            timestamp=datetime.utcnow()
        )
        db.session.add(log)
        db.session.add(new_office)
        
        try:
            db.session.commit()
            flash('Office added successfully!', 'success')
            return redirect(url_for('admin.office_stats'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while adding the office: {str(e)}', 'error')
    
    return render_template('admin/add_office.html')