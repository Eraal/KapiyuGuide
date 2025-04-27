from app.models import Inquiry, InquiryMessage, User, Office, db, OfficeAdmin, Student, CounselingSession, StudentActivityLog, SuperAdminActivityLog, OfficeLoginLog, AuditLog
from flask import Blueprint, redirect, url_for, render_template, jsonify, request, flash, Response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, current_user
from flask_socketio import emit
from app import socketio
from flask_socketio import join_room, emit
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from sqlalchemy import func, case, or_
import random
import os
from app.admin import admin_bp

################################ DASHBOARD ###################################################################



@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.role == 'admin' and not current_user.role == 'super_admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('auth.login'))
        
    total_students = User.query.filter_by(role='student').count()
    total_office_admins = User.query.filter_by(role='office_admin').count()
    total_inquiries = Inquiry.query.count()
    pending_inquiries = Inquiry.query.filter_by(status='pending').count()
    resolved_inquiries = Inquiry.query.filter_by(status='resolved').count()

    office_data = []
    offices = Office.query.all()
    for office in offices:
        inquiry_count = db.session.query(db.func.count(Inquiry.id)).filter(Inquiry.office_id == office.id).scalar()
        office_data.append({
            "name": office.name,
            "count": inquiry_count
        })
    
    top_office = (
        db.session.query(Office.name, db.func.count(Inquiry.id).label('inquiry_count'))
        .join(Inquiry)
        .group_by(Office.id)
        .order_by(db.desc('inquiry_count'))
        .first()
    )
    top_inquiry_office = top_office.name if top_office else "N/A"
    
    recent_activities = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(5).all()
    
    today = datetime.utcnow()
    upcoming_sessions = (
        CounselingSession.query
        .filter(CounselingSession.scheduled_at >= today)
        .order_by(CounselingSession.scheduled_at)
        .limit(3)
        .all()
    )
    
    system_logs = (
        AuditLog.query
        .filter(AuditLog.target_type == 'system')
        .order_by(AuditLog.timestamp.desc())
        .limit(5)
        .all()
    )
    
    weekly_labels = []
    weekly_new_inquiries = []
    weekly_resolved = []
    
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_label = day.strftime("%a")
        weekly_labels.append(day_label)
        
        new_count = (
            Inquiry.query
            .filter(func.date(Inquiry.created_at) == day.date())
            .count()
        )
        weekly_new_inquiries.append(new_count)
        
        resolved_count = (
            Inquiry.query
            .filter(
                func.date(Inquiry.created_at) == day.date(),
                Inquiry.status == 'resolved'
            )
            .count()
        )
        weekly_resolved.append(resolved_count)
    
    monthly_labels = []
    monthly_new_inquiries = []
    monthly_resolved = []
    
    for i in range(5, -1, -1):
        month_date = today.replace(day=1) - timedelta(days=i*30)
        month_label = month_date.strftime("%b")
        monthly_labels.append(month_label)
        
        month_start = month_date.replace(day=1)
        if i > 0:
            next_month = month_date.replace(day=1) + timedelta(days=32)
            month_end = next_month.replace(day=1) - timedelta(days=1)
        else:
            month_end = today
            
        new_count = (
            Inquiry.query
            .filter(
                Inquiry.created_at >= month_start,
                Inquiry.created_at <= month_end
            )
            .count()
        )
        monthly_new_inquiries.append(new_count)
        
        resolved_count = (
            Inquiry.query
            .filter(
                Inquiry.created_at >= month_start,
                Inquiry.created_at <= month_end,
                Inquiry.status == 'resolved'
            )
            .count()
        )
        monthly_resolved.append(resolved_count)

    weekly_labels = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    current_week_data = [0, 0, 0, 0, 0, 0, 0]  
    weekly_new_inquiries = current_week_data
    weekly_resolved = current_week_data.copy() 
    
    monthly_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_new_inquiries = [0] * 12  
    monthly_resolved = [0] * 12  

    return render_template(
        'admin/dashboard.html',
        offices=office_data,
        total_students=total_students,
        total_office_admins=total_office_admins,
        total_inquiries=total_inquiries,
        pending_inquiries=pending_inquiries,
        resolved_inquiries=resolved_inquiries,
        top_inquiry_office=top_inquiry_office,
        recent_activities=recent_activities,
        upcoming_sessions=upcoming_sessions,
        system_logs=system_logs,
        weekly_labels=weekly_labels,
        weekly_new_inquiries=weekly_new_inquiries,
        weekly_resolved=weekly_resolved,
        monthly_labels=monthly_labels,
        monthly_new_inquiries=monthly_new_inquiries,
        monthly_resolved=monthly_resolved
    )





@socketio.on('join_admin_room')
def handle_join_admin_room():
    if current_user.is_authenticated and current_user.role in ['admin', 'super_admin']:
        join_room('admin_room')
        print(f"Admin {current_user.email} joined admin_room")
        emit('connection_success', {
            'status': 'connected', 
            'user': current_user.email
        })

@socketio.on('connect')
def handle_connect():
    if not current_user.is_authenticated:
        return False

    if current_user.role in ['admin', 'super_admin']:
        join_room('admin_room')
        emit('connection_success', {'status': 'connected', 'user': current_user.email})

@socketio.on('new_inquiry_created')
def handle_new_inquiry(data):
    emit('new_inquiry', {
        'student_name': data.get('student_name', 'Unknown Student'),
        'subject': data.get('subject', 'New Inquiry'),
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    }, broadcast=True)

@socketio.on('inquiry_resolved')
def handle_inquiry_resolved(data):
    # Broadcast to all admins
    emit('resolved_inquiry', {
        'admin_name': data.get('admin_name', current_user.first_name if current_user.is_authenticated else 'Unknown Admin'),
        'inquiry_id': data.get('inquiry_id'),
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    }, broadcast=True)

@socketio.on('counseling_session_created')
def handle_new_session(data):
    # Broadcast to all admins
    emit('new_session', {
        'student_name': data.get('student_name', 'Unknown Student'),
        'office_name': data.get('office_name', 'Unknown Office'),
        'scheduled_at': data.get('scheduled_at'),
        'status': data.get('status', 'scheduled')
    }, broadcast=True)

@socketio.on('system_log_created')
def handle_system_log(data):
    # Broadcast to all admins
    emit('system_log', {
        'action': data.get('action', 'System Event'),
        'actor': {
            'name': data.get('actor_name', 'System'),
            'role': data.get('actor_role', 'system')
        },
        'is_success': data.get('is_success', True),
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    }, broadcast=True)

def emit_inquiry_update(inquiry, action_type):
    """
    Emit WebSocket event for inquiry updates.
    
    :param inquiry: The inquiry object
    :param action_type: 'new' or 'resolved'
    """
    if action_type == 'new':
        student = User.query.get(inquiry.student_id)
        student_name = f"{student.first_name} {student.last_name}" if student else "Unknown Student"
        
        socketio.emit('new_inquiry', {
            'student_name': student_name,
            'subject': inquiry.subject,
            'timestamp': inquiry.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }, room='admin_room')
    
    elif action_type == 'resolved':
        admin = User.query.get(inquiry.resolved_by) if inquiry.resolved_by else None
        admin_name = f"{admin.first_name} {admin.last_name}" if admin else "Unknown Admin"
        
        socketio.emit('resolved_inquiry', {
            'admin_name': admin_name,
            'inquiry_id': inquiry.id,
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }, room='admin_room')


@socketio.on('connect')
def handle_connect():
    if not current_user.is_authenticated:
        print(f"Unauthenticated connection attempt rejected")
        return False

    if current_user.role in ['admin', 'super_admin']:
        join_room('admin_room')
        print(f"Admin {current_user.email} auto-joined admin_room on connect")
        emit('connection_success', {'status': 'connected', 'user': current_user.email})


def emit_session_update(session):
    """
    Emit WebSocket event for new counseling sessions.
    
    :param session: The CounselingSession object
    """
    student = User.query.get(session.student_id)
    student_name = f"{student.first_name} {student.last_name}" if student else "Unknown Student"
    
    office = Office.query.get(session.office_id)
    office_name = office.name if office else "Unknown Office"
    
    socketio.emit('new_session', {
        'student_name': student_name,
        'office_name': office_name,
        'scheduled_at': session.scheduled_at.strftime('%Y-%m-%d %H:%M:%S'),
        'status': session.status
    }, broadcast=True)


def emit_system_log(log):
    """
    Emit WebSocket event for system logs.
    
    :param log: The AuditLog object
    """
    actor = None
    actor_name = "System"
    actor_role = "system"
    
    if log.user_id:
        actor = User.query.get(log.user_id)
        if actor:
            actor_name = f"{actor.first_name} {actor.last_name}"
            actor_role = actor.role
    
    socketio.emit('system_log', {
        'action': log.action,
        'actor': {
            'name': actor_name,
            'role': actor_role
        },
        'is_success': log.is_success if hasattr(log, 'is_success') else True,
        'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    }, broadcast=True)


@admin_bp.route('/counseling_sessions')
@login_required
def counseling_sessions():
    if not current_user.role == 'admin' and not current_user.role == 'super_admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('auth.login'))
    
    sessions = CounselingSession.query.order_by(CounselingSession.scheduled_at).all()
    return render_template('admin/counseling_sessions.html', sessions=sessions)
