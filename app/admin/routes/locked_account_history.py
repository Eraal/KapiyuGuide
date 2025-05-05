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


################################################ LOCKED ACCOUNT HISTORY #################################################

@admin_bp.route('/student_lock_history/<int:student_id>')
@login_required
def student_lock_history(student_id):
    if current_user.role != 'super_admin':
        flash('Access denied. You do not have permission to view this page.', 'danger')
        return redirect(url_for('main.index'))
    
    student = Student.query.get_or_404(student_id)
    
    # Get the lock history for this student
    lock_history = AccountLockHistory.query\
        .filter_by(user_id=student.user.id)\
        .order_by(AccountLockHistory.timestamp.desc())\
        .all()
    
    # Get admin users who locked/unlocked this account
    admin_ids = [entry.locked_by_id for entry in lock_history if entry.locked_by_id]
    admins = {admin.id: admin for admin in User.query.filter(User.id.in_(admin_ids)).all()}
    
    return render_template(
        'admin/student_lock_history.html',
        student=student,
        lock_history=lock_history,
        admins=admins
    )