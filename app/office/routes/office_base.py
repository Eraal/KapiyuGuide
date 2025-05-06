from flask import Blueprint, redirect, url_for, render_template, jsonify, request, flash, Response
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app.models import Inquiry, CounselingSession, Student, User, OfficeAdmin, Announcement
from app.utils import role_required
from .office_dashboard import get_dashboard_stats, get_chart_data
from app.office import office_bp


@office_bp.route('/dashboard')
@login_required
@role_required(['office_admin'])
def dashboard():
    """Render the office dashboard view"""
    if not hasattr(current_user, 'office_admin') or not current_user.office_admin:
        flash('Access denied. You do not have permission to view this page.', 'error')
        return redirect(url_for('main.index'))
    
    office_id = current_user.office_admin.office_id
    now = datetime.utcnow()
    
    # Get dashboard statistics
    stats = get_dashboard_stats(office_id)
    chart_data = get_chart_data(office_id)
    
    # Get recent inquiries
    recent_inquiries = Inquiry.query.filter_by(office_id=office_id).order_by(
        Inquiry.created_at.desc()
    ).limit(5).all()
    
    # Get today's sessions
    today_start = datetime.combine(now.date(), datetime.min.time())
    today_end = datetime.combine(now.date(), datetime.max.time())
    
    todays_sessions = CounselingSession.query.filter(
        CounselingSession.office_id == office_id,
        CounselingSession.scheduled_at >= today_start,
        CounselingSession.scheduled_at <= today_end
    ).order_by(CounselingSession.scheduled_at).all()
    
    # Get online staff
    online_staff = User.query.join(OfficeAdmin).filter(
        OfficeAdmin.office_id == office_id,
        User.is_online == True,
        User.last_activity > now - timedelta(minutes=15)  # Consider online if active in last 15 min
    ).all()
    
    # Get recent announcements
    recent_announcements = Announcement.query.filter(
        (Announcement.target_office_id == office_id) | (Announcement.is_public == True)
    ).order_by(Announcement.created_at.desc()).limit(3).all()
    
    # Add counts needed by the base template
    # Count of pending inquiries for the badge in sidebar
    pending_inquiries_count = Inquiry.query.filter_by(
        office_id=office_id, 
        status='pending'
    ).count()
    
    # Count of upcoming counseling sessions for the badge in sidebar
    upcoming_sessions_count = CounselingSession.query.filter(
        CounselingSession.office_id == office_id,
        CounselingSession.scheduled_at >= now,
        CounselingSession.status.in_(['scheduled', 'confirmed'])
    ).count()
    
    # Count of unread notifications
    unread_notifications_count = 0
    # You should replace this with actual notification counting logic
    # For example:
    # unread_notifications_count = Notification.query.filter_by(
    #     user_id=current_user.id, 
    #     is_read=False
    # ).count()
    
    # Get notifications for dropdown - replace with your actual model/logic
    notifications = []
    # For example:
    # notifications = Notification.query.filter_by(
    #     user_id=current_user.id
    # ).order_by(Notification.created_at.desc()).limit(5).all()
    
    return render_template('office/office_dashboard.html', 
                          stats=stats,
                          chart_data=chart_data,
                          recent_inquiries=recent_inquiries,
                          todays_sessions=todays_sessions,
                          online_staff=online_staff,
                          recent_announcements=recent_announcements,
                          pending_inquiries_count=pending_inquiries_count,
                          upcoming_sessions_count=upcoming_sessions_count,
                          unread_notifications_count=unread_notifications_count,
                          notifications=notifications,
                          now=now)


@office_bp.route('/dashboard_data')
@login_required
@role_required(['office_admin'])
def dashboard_data():
    """API endpoint to get updated dashboard data for AJAX refreshes"""
    if not hasattr(current_user, 'office_admin'):
        return jsonify({'error': 'Not authorized'}), 403
    
    office_id = current_user.office_admin.office_id
    
    stats = get_dashboard_stats(office_id)
    chart_data = get_chart_data(office_id)
    
    return jsonify({
        'stats': stats,
        'chart_data': chart_data
    })