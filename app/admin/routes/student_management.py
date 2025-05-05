from app.models import Inquiry, InquiryMessage, User, Office, db, OfficeAdmin, Student, CounselingSession, StudentActivityLog, SuperAdminActivityLog, OfficeLoginLog, AuditLog, AccountLockHistory
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


################################################ STUDENT #####################################################################

@admin_bp.route('/student_manage')
@login_required
def student_manage():
    # Check if the user is a super_admin
    if current_user.role != 'super_admin':
        flash('Access denied. You do not have permission to view this page.', 'danger')
        return redirect(url_for('main.index'))
    
    students = Student.query.join(User).all()
    
    total_students = Student.query.count()
    active_students = Student.query.join(User).filter(User.is_active == True).count()
    inactive_students = total_students - active_students

    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recently_registered = Student.query.join(User).filter(User.created_at >= seven_days_ago).count()
    
    return render_template('admin/studentmanage.html',
                           students=students,
                           total_students=total_students,
                           active_students=active_students,
                           inactive_students=inactive_students,
                           recently_registered=recently_registered)

@admin_bp.route('/toggle_student_lock', methods=['POST'])
@login_required
def toggle_student_lock():
    if current_user.role != 'super_admin':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    data = request.json
    student_id = data.get('student_id')
    should_lock = data.get('should_lock')  # True = lock, False = unlock
    reason = data.get('reason', '')  # Optional reason for locking
    
    if student_id is None or should_lock is None:
        return jsonify({'success': False, 'message': 'Missing required data'}), 400
    
    try:
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'success': False, 'message': 'Student not found'}), 404
        
        # Get the user associated with the student
        user = student.user
        
        # Toggle account lock status
        if should_lock:
            # Lock the account using the method from User model
            lock_history = user.lock_account(current_user, reason)
            action = 'locked'
        else:
            # Unlock the account using the method from User model
            unlock_history = user.unlock_account(current_user, reason)
            action = 'unlocked'
        
        # Log the super admin action
        SuperAdminActivityLog.log_action(
            super_admin=current_user,
            action=f'Student account {action}',
            target_type='user',
            target_user=user,
            details=f'Student ID: {student.id}, Student Number: {student.student_number}, Reason: {reason}',
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        
        # Create an audit log entry
        AuditLog.log_action(
            actor=current_user,
            action=f'Student account {action}',
            target_type='user',
            status=f'Account {action}',
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        
        db.session.commit()
        
        # Return success response with updated status
        return jsonify({
            'success': True, 
            'message': f'Student account has been {action}',
            'account_locked': user.account_locked,
            'lock_reason': user.lock_reason,
            'locked_at': user.locked_at.strftime('%Y-%m-%d %H:%M:%S') if user.locked_at else None
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/view_student/<int:student_id>', methods=['GET', 'POST'])
@login_required
def view_student(student_id):
    if current_user.role != 'super_admin':
        flash('Access denied. You do not have permission to view this page.', 'danger')
        return redirect(url_for('main.index'))
    
    student = Student.query.get_or_404(student_id)
    
    if request.method == 'POST':
        try:
            student.user.first_name = request.form.get('first_name')
            student.user.middle_name = request.form.get('middle_name')
            student.user.last_name = request.form.get('last_name')
            student.user.email = request.form.get('email')
            
            student.phone_number = request.form.get('phone_number')
            student.address = request.form.get('address')
            

            if 'reset_password' in request.form:
 
                new_password = ''.join(random.choices('0123456789', k=4))

                student.user.password_hash = generate_password_hash(new_password)
                
                flash(f'Password has been reset to: {new_password}', 'success')
            
            db.session.commit()
            flash('Student information updated successfully', 'success')
            return redirect(url_for('admin.student_manage'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating student: {str(e)}', 'danger')
    
    return render_template('admin/view_student.html', student=student)
