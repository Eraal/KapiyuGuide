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
from app.admin.utils import save_profile_picture, delete_profile_picture
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators
from flask_wtf.file import FileField, FileAllowed
import pyotp 

# Create forms for account settings
class PersonalInfoForm(FlaskForm):
    first_name = StringField('First Name', [validators.DataRequired()])
    middle_name = StringField('Middle Name')
    last_name = StringField('Last Name', [validators.DataRequired()])
    email = StringField('Email', [validators.DataRequired(), validators.Email()])

class PasswordChangeForm(FlaskForm):
    current_password = PasswordField('Current Password', [validators.DataRequired()])
    new_password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.Length(min=8),
        validators.Regexp(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]', 
                          message='Password must contain letters, numbers, and special characters')
    ])
    confirm_password = PasswordField('Confirm Password', [
        validators.DataRequired(),
        validators.EqualTo('new_password', message='Passwords must match')
    ])

class ProfilePicForm(FlaskForm):
    profile_pic = FileField('Profile Picture', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')
    ])

@admin_bp.route('/account-settings')
@login_required
def account_settings():
    # Check if user is authorized (super admin)
    if current_user.role != 'super_admin':
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    # Create the forms
    personal_form = PersonalInfoForm(obj=current_user)
    password_form = PasswordChangeForm()
    profile_pic_form = ProfilePicForm()
    
    # Check if two-factor auth is enabled for the user
    # This is a placeholder - implement based on your 2FA system
    tfa_enabled = False
    
    return render_template('admin/account_settings.html', 
                          personal_form=personal_form,
                          password_form=password_form,
                          profile_pic_form=profile_pic_form,
                          tfa_enabled=tfa_enabled)

@admin_bp.route('/update-personal-info', methods=['POST'])
@login_required
def update_personal_info():
    if current_user.role != 'super_admin':
        flash('Permission denied.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    form = PersonalInfoForm()
    if form.validate_on_submit():
        try:
            current_user.first_name = form.first_name.data
            current_user.middle_name = form.middle_name.data
            current_user.last_name = form.last_name.data
            current_user.email = form.email.data
            
            # Log the action
            SuperAdminActivityLog.log_action(
                super_admin=current_user,
                action="Updated Personal Info",
                target_type="user",
                target_user=current_user,
                details="Updated personal information",
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string
            )
            
            db.session.commit()
            flash('Personal information updated successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'error')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", 'error')
    
    return redirect(url_for('admin.account_settings'))

@admin_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    if current_user.role != 'super_admin':
        flash('Permission denied.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    form = PasswordChangeForm()
    if form.validate_on_submit():
        # Check if current password is correct
        if check_password_hash(current_user.password_hash, form.current_password.data):
            try:
                # Update password
                current_user.password_hash = generate_password_hash(form.new_password.data)
                
                # Log the action
                SuperAdminActivityLog.log_action(
                    super_admin=current_user,
                    action="Changed Password",
                    target_type="user",
                    target_user=current_user,
                    details="Password changed",
                    ip_address=request.remote_addr,
                    user_agent=request.user_agent.string
                )
                
                db.session.commit()
                flash('Password changed successfully.', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'An error occurred: {str(e)}', 'error')
        else:
            flash('Current password is incorrect.', 'error')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", 'error')
    
    return redirect(url_for('admin.account_settings'))

@admin_bp.route('/update-profile-picture', methods=['POST'])
@login_required
def update_profile_picture():
    if current_user.role != 'super_admin':
        flash('Permission denied.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    form = ProfilePicForm()
    if form.validate_on_submit():
        try:
            if form.profile_pic.data:
                # Save the new profile picture
                filename = save_profile_picture(form.profile_pic.data)
                
                # Delete old profile picture if exists
                if current_user.profile_pic:
                    delete_profile_picture(current_user.profile_pic)
                
                current_user.profile_pic = filename
                
                # Log the action
                SuperAdminActivityLog.log_action(
                    super_admin=current_user,
                    action="Updated Profile Picture",
                    target_type="user",
                    target_user=current_user,
                    details="Updated profile picture",
                    ip_address=request.remote_addr,
                    user_agent=request.user_agent.string
                )
                
                db.session.commit()
                flash('Profile picture updated successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'error')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", 'error')
    
    return redirect(url_for('admin.account_settings'))

@admin_bp.route('/remove-profile-picture', methods=['POST'])
@login_required
def remove_profile_picture():
    if current_user.role != 'super_admin' or not current_user.profile_pic:
        flash('Permission denied or no profile picture to remove.', 'error')
        return redirect(url_for('admin.account_settings'))
    
    try:
        # Delete the profile picture file
        delete_profile_picture(current_user.profile_pic)
        
        # Update user record
        current_user.profile_pic = None
        
        # Log the action
        SuperAdminActivityLog.log_action(
            super_admin=current_user,
            action="Removed Profile Picture",
            target_type="user",
            target_user=current_user,
            details="Removed profile picture",
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        
        db.session.commit()
        flash('Profile picture removed successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'error')
    
    return redirect(url_for('admin.account_settings'))

@admin_bp.route('/setup-two-factor', methods=['GET', 'POST'])
@login_required
def setup_two_factor():
    if current_user.role != 'super_admin':
        flash('Permission denied.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    # Implement two-factor authentication setup here
    # This is a placeholder - you'd need to implement the actual 2FA logic
    if request.method == 'POST':
        # Process 2FA setup
        flash('Two-factor authentication setup successful.', 'success')
        return redirect(url_for('admin.account_settings'))
    
    # Generate new secret key for 2FA setup
    secret_key = pyotp.random_base32()
    # Create provisioning URI for QR code
    totp_uri = pyotp.totp.TOTP(secret_key).provisioning_uri(
        name=current_user.email,
        issuer_name="KapiyuGuide"
    )
    
    return render_template('admin/setup_two_factor.html', 
                           secret_key=secret_key, 
                           totp_uri=totp_uri)

@admin_bp.route('/disable-two-factor', methods=['POST'])
@login_required
def disable_two_factor():
    if current_user.role != 'super_admin':
        return jsonify({'success': False, 'message': 'Permission denied'})
    
    try:
        # Disable 2FA for the user
        # This is a placeholder - implement your 2FA disabling logic
        
        # Log the action
        SuperAdminActivityLog.log_action(
            super_admin=current_user,
            action="Disabled Two-Factor Auth",
            target_type="user",
            target_user=current_user,
            details="Disabled two-factor authentication",
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@admin_bp.route('/login-history')
@login_required
def login_history():
    if current_user.role != 'super_admin':
        flash('Permission denied.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    # Get login history for the current user
    # This is a placeholder - implement based on your login tracking system
    login_logs = AuditLog.query.filter(
        AuditLog.actor_id == current_user.id,
        AuditLog.action.in_(['Login', 'Logout'])
    ).order_by(AuditLog.timestamp.desc()).limit(30).all()
    
    return render_template('admin/login_history.html', login_logs=login_logs)

@admin_bp.route('/deactivate-account', methods=['POST'])
@login_required
def deactivate_account():
    if current_user.role != 'super_admin':
        flash('Permission denied.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    try:
        # Check if there's at least one other active super admin
        other_admins = User.query.filter(
            User.role == 'super_admin',
            User.is_active == True,
            User.id != current_user.id
        ).count()
        
        if other_admins == 0:
            flash('Cannot deactivate account: You are the only active super admin.', 'error')
            return redirect(url_for('admin.account_settings'))
        
        # Deactivate the account
        current_user.is_active = False
        
        # Log the action from another super admin's perspective (since this is a self-deactivation)
        SuperAdminActivityLog.log_action(
            super_admin=current_user,
            action="Self-Deactivated Account",
            target_type="user",
            target_user=current_user,
            details="Admin deactivated their own account",
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        
        db.session.commit()
        flash('Your account has been deactivated. You will be logged out.', 'info')
        
        # Log the user out
        return redirect(url_for('auth.logout'))
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'error')
        
    return redirect(url_for('admin.account_settings'))
