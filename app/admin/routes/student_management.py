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

@admin_bp.route('/toggle_student_status', methods=['POST'])
@login_required
def toggle_student_status():
    if current_user.role != 'super_admin':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    data = request.json
    student_id = data.get('student_id')
    is_active = data.get('is_active')
    
    if student_id is None or is_active is None:
        return jsonify({'success': False, 'message': 'Missing required data'}), 400
    
    try:
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'success': False, 'message': 'Student not found'}), 404
        
        student.user.is_active = bool(is_active)
        db.session.commit()
        
        status = 'activated' if is_active else 'deactivated'
        flash(f'Student account has been {status}', 'success')
        
        return jsonify({'success': True, 'message': 'Student status updated successfully'})
    
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
