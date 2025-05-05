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

################################# EDIT OFFICE ###############################################

# Edit Office Route (Updated with Better AJAX Handling)
@admin_bp.route('/office/<int:office_id>/edit/', methods=['GET', 'POST'])
@login_required
def edit_office(office_id):
    if current_user.role != 'super_admin':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'You do not have permission to access this page.'})
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('main.index'))
    
    office = Office.query.get_or_404(office_id)
    
    if request.method == 'POST':
        try:
            office.name = request.form.get('name')
            office.description = request.form.get('description')

            # Set supports_video if provided
            supports_video = request.form.get('supports_video')
            if supports_video:
                office.supports_video = supports_video.lower() == 'true'
            
            # Log activity
            log = SuperAdminActivityLog(
                super_admin_id=current_user.id,
                action=f"Edited office: {office.name}",
                timestamp=datetime.utcnow()
            )
            db.session.add(log)
            db.session.commit()
            
            # Check if it's an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': True,
                    'message': 'Office updated successfully!',
                    'office': {
                        'id': office.id,
                        'name': office.name,
                        'description': office.description,
                        'supports_video': office.supports_video
                    }
                })
                
            flash('Office updated successfully!', 'success')
            return redirect(url_for('admin.view_office_details', office_id=office.id))
        except Exception as e:
            db.session.rollback()
            
            # Check if it's an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': False,
                    'message': f'An error occurred while updating the office: {str(e)}'
                }), 400  # Return appropriate error status code
                
            flash(f'An error occurred while updating the office: {str(e)}', 'error')
    
    # For GET requests, just render the template with the office details
    if request.method == 'GET':
        return render_template('admin/edit_office.html', office=office)
    
    # If it's a non-AJAX POST request that failed, render the form again
    return render_template('admin/edit_office.html', office=office)

# Toggle Office Status (Modified since Office doesn't have is_active field directly)
@admin_bp.route('/office/<int:office_id>/toggle_status/', methods=['POST'])
@login_required
def toggle_office_status(office_id):
    if current_user.role != 'super_admin':
        flash('You do not have permission to perform this action.', 'error')
        return redirect(url_for('admin.office_stats'))
    
    office = Office.query.get_or_404(office_id)
    
    # Since Office doesn't have is_active field, we'll handle it differently
    # We could implement this by checking if an office has any active admins
    has_active_admins = False
    for admin in office.office_admins:
        if admin.user.is_active:
            has_active_admins = True
            break
    
    status_text = "disabled" if has_active_admins else "enabled"
    action_text = "Disabled" if has_active_admins else "Enabled"
    
    # If we want to disable the office, we'll deactivate all admin accounts
    if has_active_admins:
        for admin in office.office_admins:
            admin.user.is_active = False
    else:
        # If we want to enable, we need to ensure there's at least one active admin
        # If none, we'll notify the user
        if not office.office_admins:
            flash('Cannot enable office without assigned admins.', 'warning')
            return redirect(url_for('admin.office_stats'))
        # Otherwise, activate the first admin
        office.office_admins[0].user.is_active = True
    
    # Log activity
    log = SuperAdminActivityLog(
        super_admin_id=current_user.id,
        action=f"{action_text} office: {office.name}",
        timestamp=datetime.utcnow()
    )
    db.session.add(log)
    
    try:
        db.session.commit()
        flash(f'Office {status_text} successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while updating the office status: {str(e)}', 'error')
    
    return redirect(url_for('admin.office_stats'))