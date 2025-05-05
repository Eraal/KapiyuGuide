from app.models import (
    Inquiry, InquiryMessage, User, Office, db, OfficeAdmin, 
    Student, CounselingSession, StudentActivityLog, SuperAdminActivityLog, 
    OfficeLoginLog, AuditLog
)
from flask import Blueprint, redirect, url_for, render_template, jsonify, request, flash, Response
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func, case, or_
from app.admin import admin_bp
from app.websockets.admin_sockets import emit_inquiry_update, emit_session_update, emit_system_log, update_dashboard_stats

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.role == 'office_admin' and not current_user.role == 'super_admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('auth.login'))
        
    # Dashboard statistics
    total_students = User.query.filter_by(role='student').count()
    total_office_admins = User.query.filter_by(role='office_admin').count()
    total_inquiries = Inquiry.query.count()
    pending_inquiries = Inquiry.query.filter_by(status='pending').count()
    resolved_inquiries = Inquiry.query.filter_by(status='resolved').count()

    # Office data
    office_data = []
    offices = Office.query.all()
    for office in offices:
        inquiry_count = db.session.query(db.func.count(Inquiry.id)).filter(Inquiry.office_id == office.id).scalar()
        office_data.append({
            "name": office.name,
            "count": inquiry_count
        })
    
    # Find top office by inquiry count
    top_office = (
        db.session.query(Office.name, db.func.count(Inquiry.id).label('inquiry_count'))
        .join(Inquiry)
        .group_by(Office.id)
        .order_by(db.desc('inquiry_count'))
        .first()
    )
    top_inquiry_office = top_office.name if top_office else "N/A"
    
    # Recent activities and logs
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
    
    # Chart data initialization
    weekly_labels = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    current_week_data = [0, 0, 0, 0, 0, 0, 0]  
    weekly_new_inquiries = current_week_data.copy()  # Use copy to avoid reference issues
    weekly_resolved = current_week_data.copy() 
    
    monthly_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_new_inquiries = [0] * 12  
    monthly_resolved = [0] * 12  
    
    # Calculate weekly inquiry data
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_of_week = day.weekday()
        
        # Adjust for Python's weekday (0=Monday) to our display (0=Sunday)
        chart_index = (day_of_week + 1) % 7
        
        new_count = (
            Inquiry.query
            .filter(func.date(Inquiry.created_at) == day.date())
            .count()
        )
        
        # For resolved inquiries, we count those that have status='resolved'
        # and were updated (not using resolved_at since it doesn't exist)
        resolved_count = (
            Inquiry.query
            .filter(
                func.date(Inquiry.created_at) == day.date(),
                Inquiry.status == 'resolved'
            )
            .count()
        )
        
        # Update the data arrays
        weekly_new_inquiries[chart_index] = new_count
        weekly_resolved[chart_index] = resolved_count
    
    # Calculate monthly data
    current_month = today.month - 1  # 0-based index for months
    for i in range(12):
        month_index = (current_month - 11 + i) % 12  # Get the month index, wrapping around
        year_offset = 0 if month_index <= current_month else -1
        query_year = today.year + year_offset
        
        # Month in database is 1-based
        db_month = month_index + 1
        
        # Count new inquiries for this month
        monthly_new_inquiries[i] = Inquiry.query.filter(
            func.extract('year', Inquiry.created_at) == query_year,
            func.extract('month', Inquiry.created_at) == db_month
        ).count()
        
        # Count resolved inquiries for this month
        monthly_resolved[i] = Inquiry.query.filter(
            func.extract('year', Inquiry.created_at) == query_year,
            func.extract('month', Inquiry.created_at) == db_month,
            Inquiry.status == 'resolved'
        ).count()

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

@admin_bp.route('/counseling_sessions')
@login_required
def counseling_sessions():
    if not current_user.role == 'office_admin' and not current_user.role == 'super_admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('auth.login'))
    
    sessions = CounselingSession.query.order_by(CounselingSession.scheduled_at).all()
    return render_template('admin/counseling_sessions.html', sessions=sessions)

# Example API endpoint that will trigger a WebSocket event
@admin_bp.route('/api/inquiries/<int:inquiry_id>/resolve', methods=['POST'])
@login_required
def resolve_inquiry(inquiry_id):
    if not current_user.role in ['office_admin', 'super_admin']:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
        
    inquiry = Inquiry.query.get_or_404(inquiry_id)
    inquiry.status = 'resolved'
    inquiry.resolved_by = current_user.id
    # No resolved_at field in the model, so we don't set it
    
    # Log this action
    AuditLog.log_action(
        actor=current_user,
        action="Resolve Inquiry",
        target_type="inquiry",
        target_id=inquiry.id,
        is_success=True
    )
    
    db.session.commit()
    
    emit_inquiry_update(inquiry, 'resolved')
    update_dashboard_stats()
    
    return jsonify({'status': 'success', 'message': 'Inquiry resolved successfully'})

@admin_bp.route('/api/sessions', methods=['POST'])
@login_required
def create_session():
    if not current_user.role in ['office_admin', 'super_admin']:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    
    try:
        data = request.json
        student_id = data.get('student_id')
        office_id = data.get('office_id')
        counselor_id = data.get('counselor_id')
        scheduled_at = datetime.fromisoformat(data.get('scheduled_at'))
        
        session = CounselingSession(
            student_id=student_id,
            office_id=office_id,
            counselor_id=counselor_id if counselor_id else None,
            scheduled_at=scheduled_at,
            status='scheduled',
            created_by=current_user.id
        )
        
        db.session.add(session)
        
        # Log this action
        AuditLog.log_action(
            actor=current_user,
            action="Create Counseling Session",
            target_type="session",
            target_id=session.id if session.id else None,
            is_success=True
        )
        
        db.session.commit()
        
        # Emit WebSocket event
        emit_session_update(session, 'new')
        
        # Update dashboard stats for super admins
        update_dashboard_stats()
        
        return jsonify({'status': 'success', 'message': 'Session created successfully'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@admin_bp.route('/api/sessions/<int:session_id>/update', methods=['PUT'])
@login_required
def update_session(session_id):
    if not current_user.role in ['office_admin', 'super_admin']:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    
    try:
        session = CounselingSession.query.get_or_404(session_id)
        data = request.json
        
        if 'status' in data:
            session.status = data['status']
        
        if 'counselor_id' in data:
            session.counselor_id = data['counselor_id']
        
        if 'scheduled_at' in data and data['scheduled_at']:
            session.scheduled_at = datetime.fromisoformat(data['scheduled_at'])
        
        # Log this action
        AuditLog.log_action(
            actor=current_user,
            action="Update Counseling Session",
            target_type="session",
            target_id=session.id,
            is_success=True
        )
        
        db.session.commit()
        
        # Emit WebSocket event
        emit_session_update(session, 'updated')
        
        # Update dashboard stats for super admins
        update_dashboard_stats()
        
        return jsonify({'status': 'success', 'message': 'Session updated successfully'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@admin_bp.route('/api/dashboard/stats', methods=['GET'])
@login_required
def get_dashboard_stats():
    """API endpoint for fetching dashboard statistics"""
    if not current_user.role in ['office_admin', 'super_admin']:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    
    total_students = User.query.filter_by(role='student').count()
    total_office_admins = User.query.filter_by(role='office_admin').count()
    total_inquiries = Inquiry.query.count()
    pending_inquiries = Inquiry.query.filter_by(status='pending').count()
    resolved_inquiries = Inquiry.query.filter_by(status='resolved').count()
    
    # Get offices with their inquiry counts
    offices = Office.query.all()
    office_data = []
    for office in offices:
        inquiry_count = Inquiry.query.filter_by(office_id=office.id).count()
        session_count = CounselingSession.query.filter_by(office_id=office.id).count()
        office_data.append({
            "id": office.id,
            "name": office.name,
            "inquiry_count": inquiry_count,
            "session_count": session_count
        })
    
    # Get upcoming sessions
    today = datetime.utcnow()
    upcoming_sessions = (
        CounselingSession.query
        .filter(CounselingSession.scheduled_at >= today)
        .order_by(CounselingSession.scheduled_at)
        .limit(5)
        .all()
    )
    
    upcoming_session_data = []
    for session in upcoming_sessions:
        student = User.query.join(Student).filter(Student.id == session.student_id).first()
        office = Office.query.get(session.office_id)
        counselor = User.query.get(session.counselor_id) if session.counselor_id else None
        
        upcoming_session_data.append({
            "id": session.id,
            "student_name": student.get_full_name() if student else "Unknown Student",
            "office_name": office.name if office else "Unknown Office",
            "counselor_name": counselor.get_full_name() if counselor else "Unassigned",
            "scheduled_at": session.scheduled_at.strftime('%Y-%m-%d %H:%M:%S'),
            "status": session.status
        })
    
    return jsonify({
        'status': 'success',
        'data': {
            'total_students': total_students,
            'total_office_admins': total_office_admins,
            'total_inquiries': total_inquiries,
            'pending_inquiries': pending_inquiries,
            'resolved_inquiries': resolved_inquiries,
            'offices': office_data,
            'upcoming_sessions': upcoming_session_data
        }
    })