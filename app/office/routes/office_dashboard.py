from app.models import (
    Inquiry, InquiryMessage, User, Office, db, OfficeAdmin, 
    Student, CounselingSession, StudentActivityLog, SuperAdminActivityLog, 
    OfficeLoginLog, AuditLog, Announcement
)
from flask import Blueprint, redirect, url_for, render_template, jsonify, request, flash, Response
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import time  # Add missing import for time module
from sqlalchemy import func, case, desc, or_  # Add missing desc import
from app.office import office_bp


def get_dashboard_stats(office_id):
    """Calculate dashboard statistics for a specific office"""
    now = datetime.utcnow()
    one_week_ago = now - timedelta(days=7)
    one_month_ago = now - timedelta(days=30)
    two_months_ago = now - timedelta(days=60)
    
    # Pending inquiries
    pending_inquiries = Inquiry.query.filter_by(
        office_id=office_id, status='pending'
    ).count()
    
    # Pending inquiries last week for comparison
    pending_inquiries_last_week = Inquiry.query.filter(
        Inquiry.office_id == office_id,
        Inquiry.status == 'pending',
        Inquiry.created_at > one_week_ago,
        Inquiry.created_at <= now - timedelta(days=1)
    ).count()
    
    # Calculate % change
    if pending_inquiries_last_week > 0:
        pending_inquiries_change = ((pending_inquiries - pending_inquiries_last_week) / 
                                   pending_inquiries_last_week) * 100
    else:
        pending_inquiries_change = 0
    
    # Upcoming sessions
    tomorrow = now + timedelta(days=1)
    upcoming_sessions = CounselingSession.query.filter(
        CounselingSession.office_id == office_id,
        CounselingSession.status.in_(['pending', 'confirmed']),
        CounselingSession.scheduled_at > now,
        CounselingSession.scheduled_at < tomorrow
    ).count()
    
    # Find next scheduled session time
    next_session = CounselingSession.query.filter(
        CounselingSession.office_id == office_id,
        CounselingSession.scheduled_at > now
    ).order_by(CounselingSession.scheduled_at).first()
    
    next_session_time = "No upcoming sessions"
    if next_session:
        # Format as "2h 15m" if today, otherwise "Tomorrow 14:30" or "May 12, 14:30"
        if next_session.scheduled_at.date() == now.date():
            time_diff = next_session.scheduled_at - now
            hours = time_diff.seconds // 3600
            minutes = (time_diff.seconds % 3600) // 60
            if hours > 0:
                next_session_time = f"{hours}h {minutes}m"
            else:
                next_session_time = f"{minutes}m"
        elif next_session.scheduled_at.date() == (now + timedelta(days=1)).date():
            next_session_time = f"Tomorrow {next_session.scheduled_at.strftime('%H:%M')}"
        else:
            next_session_time = next_session.scheduled_at.strftime('%b %d, %H:%M')
    
    # Students served this month (resolved inquiries or completed sessions)
    students_served_month = db.session.query(func.count(func.distinct(Student.id))).join(
        Inquiry, Student.id == Inquiry.student_id
    ).filter(
        Inquiry.office_id == office_id,
        Inquiry.status == 'resolved',
        Inquiry.created_at > one_month_ago
    ).scalar()
    
    students_served_month += db.session.query(func.count(func.distinct(Student.id))).join(
        CounselingSession, Student.id == CounselingSession.student_id
    ).filter(
        CounselingSession.office_id == office_id,
        CounselingSession.status == 'completed',
        CounselingSession.scheduled_at > one_month_ago
    ).scalar()
    
    # Students served previous month
    students_served_prev_month = db.session.query(
        func.count(func.distinct(Student.id))
    ).join(
        Inquiry, Student.id == Inquiry.student_id
    ).filter(
        Inquiry.office_id == office_id,
        Inquiry.status == 'resolved',
        Inquiry.created_at > two_months_ago,
        Inquiry.created_at <= one_month_ago
    ).scalar()
    
    students_served_prev_month += db.session.query(
        func.count(func.distinct(Student.id))
    ).join(
        CounselingSession, Student.id == CounselingSession.student_id
    ).filter(
        CounselingSession.office_id == office_id,
        CounselingSession.status == 'completed',
        CounselingSession.scheduled_at > two_months_ago,
        CounselingSession.scheduled_at <= one_month_ago
    ).scalar()
    
    # Calculate percentage change for students served
    if students_served_prev_month > 0:
        students_served_change = ((students_served_month - students_served_prev_month) / 
                                  students_served_prev_month) * 100
    else:
        students_served_change = 0
    
    # Staff statistics
    total_staff = OfficeAdmin.query.filter_by(office_id=office_id).count()
    staff_online = User.query.join(OfficeAdmin).filter(
        OfficeAdmin.office_id == office_id,
        User.is_online == True,
        User.last_activity > now - timedelta(minutes=15)  # Consider online if active in last 15 min
    ).count()
    
    return {
        'pending_inquiries': pending_inquiries,
        'pending_inquiries_change': round(pending_inquiries_change),
        'upcoming_sessions': upcoming_sessions,
        'next_session_time': next_session_time,
        'students_served_month': students_served_month,
        'students_served_change': round(students_served_change),
        'staff_online': staff_online,
        'total_staff': total_staff
    }

def get_chart_data(office_id):
    """Get activity chart data for the last 7-14 days for a specific office"""
    now = datetime.utcnow()
    labels = []
    inquiries_data = []
    sessions_data = []
    
    # Get data for the last 7 days
    for i in range(6, -1, -1):
        day = now - timedelta(days=i)
        day_start = datetime.combine(day.date(), datetime.min.time())  # Fixed: use datetime.min.time()
        day_end = datetime.combine(day.date(), datetime.max.time())    # Fixed: use datetime.max.time()
        
        # Format label as "Mon", "Tue", etc.
        labels.append(day.strftime('%a'))
        
        # Count inquiries created on this day
        inquiries_count = Inquiry.query.filter(
            Inquiry.office_id == office_id,
            Inquiry.created_at >= day_start,
            Inquiry.created_at <= day_end
        ).count()
        inquiries_data.append(inquiries_count)
        
        # Count counseling sessions scheduled on this day
        sessions_count = CounselingSession.query.filter(
            CounselingSession.office_id == office_id,
            CounselingSession.scheduled_at >= day_start,
            CounselingSession.scheduled_at <= day_end
        ).count()
        sessions_data.append(sessions_count)
    
    return {
        'labels': labels,
        'inquiries': inquiries_data,
        'sessions': sessions_data
    }


# Function to get office context - assumed to be defined elsewhere
def get_office_context():
    """Get common context data needed across office views"""
    # This is a placeholder since the original function isn't provided
    return {}

# Additional routes for the office dashboard
@office_bp.route('/inquiries')
@login_required
def inquiries():
    """View all inquiries for the office"""
    if current_user.role != 'office_admin':
        flash('Access denied. You do not have permission to view this page.', 'error')
        return redirect(url_for('main.index'))
    
    office_id = current_user.office_admin.office_id
    
    # Get filter parameters
    status = request.args.get('status', 'all')
    date_range = request.args.get('date_range', '7d')  # Default to last 7 days
    sort_by = request.args.get('sort_by', 'newest')
    page = request.args.get('page', 1, type=int)
    
    # Base query
    query = Inquiry.query.filter_by(office_id=office_id)
    
    # Apply status filter
    if status != 'all':
        query = query.filter_by(status=status)
    
    # Apply date range filter
    now = datetime.utcnow()
    if date_range == '7d':
        query = query.filter(Inquiry.created_at >= now - timedelta(days=7))
    elif date_range == '30d':
        query = query.filter(Inquiry.created_at >= now - timedelta(days=30))
    elif date_range == '90d':
        query = query.filter(Inquiry.created_at >= now - timedelta(days=90))
    
    # Apply sorting
    if sort_by == 'newest':
        query = query.order_by(desc(Inquiry.created_at))
    elif sort_by == 'oldest':
        query = query.order_by(Inquiry.created_at)
    
    # Paginate results
    inquiries = query.paginate(page=page, per_page=20, error_out=False)
    
    # Get stats for sidebar
    pending_count = Inquiry.query.filter_by(office_id=office_id, status='pending').count()
    in_progress_count = Inquiry.query.filter_by(office_id=office_id, status='in_progress').count()
    resolved_count = Inquiry.query.filter_by(office_id=office_id, status='resolved').count()
    
    context = get_office_context()
    context.update({
        'inquiries': inquiries,
        'status': status,
        'date_range': date_range,
        'sort_by': sort_by,
        'pending_count': pending_count,
        'in_progress_count': in_progress_count,
        'resolved_count': resolved_count,
    })
    
    return render_template('office/inquiries.html', **context)


@office_bp.route('/appointments')
@login_required
def appointments():
    """View all counseling appointments for the office"""
    if current_user.role != 'office_admin':
        flash('Access denied. You do not have permission to view this page.', 'error')
        return redirect(url_for('main.index'))
    
    office_id = current_user.office_admin.office_id
    
    # Get filter parameters
    status = request.args.get('status', 'upcoming')
    date_range = request.args.get('date_range', '7d')  # Default to next 7 days
    counselor_id = request.args.get('counselor_id', 'all')
    page = request.args.get('page', 1, type=int)
    
    # Base query
    query = CounselingSession.query.filter_by(office_id=office_id)
    
    # Apply status filter
    now = datetime.utcnow()
    if status == 'upcoming':
        query = query.filter(
            CounselingSession.status.in_(['pending', 'confirmed']),
            CounselingSession.scheduled_at > now
        )
    elif status == 'today':
        today_start = datetime.combine(now.date(), datetime.min.time())  # Fixed: use datetime.min.time()
        today_end = datetime.combine(now.date(), datetime.max.time())    # Fixed: use datetime.max.time()
        query = query.filter(
            CounselingSession.scheduled_at >= today_start,
            CounselingSession.scheduled_at <= today_end
        )
    elif status == 'past':
        query = query.filter(
            CounselingSession.status == 'completed'
        )
    elif status == 'cancelled':
        query = query.filter(
            CounselingSession.status == 'cancelled'
        )
    elif status != 'all':
        query = query.filter_by(status=status)
    
    # Apply date range filter
    if date_range == '7d' and status == 'upcoming':
        query = query.filter(CounselingSession.scheduled_at <= now + timedelta(days=7))
    elif date_range == '30d' and status == 'upcoming':
        query = query.filter(CounselingSession.scheduled_at <= now + timedelta(days=30))
    elif date_range == '7d' and status == 'past':
        query = query.filter(CounselingSession.scheduled_at >= now - timedelta(days=7))
    elif date_range == '30d' and status == 'past':
        query = query.filter(CounselingSession.scheduled_at >= now - timedelta(days=30))
    
    # Apply counselor filter
    if counselor_id != 'all':
        query = query.filter_by(counselor_id=int(counselor_id))
    
    # Always sort by scheduled_at date
    if status == 'upcoming' or status == 'today':
        query = query.order_by(CounselingSession.scheduled_at)
    else:
        query = query.order_by(desc(CounselingSession.scheduled_at))
    
    # Paginate results
    sessions = query.paginate(page=page, per_page=20, error_out=False)
    
    # Get counselors for filter dropdown
    counselors = User.query.join(OfficeAdmin).filter(
        OfficeAdmin.office_id == office_id,
        User.role == 'office_admin'
    ).all()
    
    # Get stats for sidebar
    today_start = datetime.combine(now.date(), datetime.min.time())  # Fixed: use datetime.min.time()
    today_end = datetime.combine(now.date(), datetime.max.time())    # Fixed: use datetime.max.time()
    
    today_count = CounselingSession.query.filter(
        CounselingSession.office_id == office_id,
        CounselingSession.scheduled_at >= today_start,
        CounselingSession.scheduled_at <= today_end
    ).count()
    
    upcoming_count = CounselingSession.query.filter(
        CounselingSession.office_id == office_id,
        CounselingSession.status.in_(['pending', 'confirmed']),
        CounselingSession.scheduled_at > now
    ).count()
    
    past_count = CounselingSession.query.filter(
        CounselingSession.office_id == office_id,
        CounselingSession.status == 'completed'
    ).count()
    
    context = get_office_context()
    context.update({
        'sessions': sessions,
        'status': status,
        'date_range': date_range,
        'counselor_id': counselor_id,
        'counselors': counselors,
        'today_count': today_count,
        'upcoming_count': upcoming_count,
        'past_count': past_count,
    })
    
    return render_template('office/appointments.html', **context)

@office_bp.route('/staff')
@login_required
def staff():
    """View staff information for the office"""
    if current_user.role != 'office_admin':
        flash('Access denied. You do not have permission to view this page.', 'error')
        return redirect(url_for('main.index'))
    
    office_id = current_user.office_admin.office_id
    
    # Get all staff members for this office
    staff_members = User.query.join(OfficeAdmin).filter(
        OfficeAdmin.office_id == office_id,
        User.role == 'office_admin'
    ).all()
    
    # Get activity stats for each staff member
    staff_data = []
    now = datetime.utcnow()
    one_month_ago = now - timedelta(days=30)
    
    for staff in staff_members:
        # Count inquiries handled
        inquiries_count = Inquiry.query.filter(
            Inquiry.office_id == office_id,
            Inquiry.handled_by_id == staff.id,  # Note: This field might not exist in your model
            Inquiry.status == 'resolved',
            Inquiry.updated_at > one_month_ago  # Note: This field might need verification
        ).count()
        
        # Count counseling sessions conducted
        sessions_count = CounselingSession.query.filter(
            CounselingSession.office_id == office_id,
            CounselingSession.counselor_id == staff.id,
            CounselingSession.status == 'completed',
            CounselingSession.scheduled_at > one_month_ago  # Using scheduled_at since completed_at might not exist
        ).count()
        
        # Get last login time
        last_login = OfficeLoginLog.query.filter_by(
            user_id=staff.id  # Note: This should match your OfficeLoginLog schema
        ).order_by(desc(OfficeLoginLog.login_time)).first()
        
        staff_data.append({
            'user': staff,
            'inquiries_count': inquiries_count,
            'sessions_count': sessions_count,
            'total_activity': inquiries_count + sessions_count,
            'last_login': last_login.login_time if last_login else None,
            'is_online': staff.is_online and staff.last_activity > now - timedelta(minutes=15)
        })
    
    # Sort by activity
    staff_data.sort(key=lambda x: x['total_activity'], reverse=True)
    
    context = get_office_context()
    context.update({
        'staff_data': staff_data,
        'office': Office.query.get(office_id)
    })
    
    return render_template('office/office_staff.html', **context)

@office_bp.route('/announcements')
@login_required
def announcements():
    """View announcements for the office"""
    if current_user.role != 'office_admin':
        flash('Access denied. You do not have permission to view this page.', 'error')
        return redirect(url_for('main.index'))
    
    office_id = current_user.office_admin.office_id
    page = request.args.get('page', 1, type=int)
    
    # Get all announcements for this office or public announcements
    announcements = Announcement.query.filter(
        (Announcement.target_office_id == office_id) | 
        (Announcement.is_public == True)
    ).order_by(desc(Announcement.created_at)).paginate(
        page=page, per_page=10, error_out=False
    )
    
    context = get_office_context()
    context.update({
        'announcements': announcements
    })
    
    return render_template('office/announcements.html', **context)

@office_bp.route('/view_appointment/<int:session_id>')
@login_required
def view_appointment(session_id):
    """View a specific counseling session"""
    if current_user.role != 'office_admin':
        flash('Access denied. You do not have permission to view this page.', 'error')
        return redirect(url_for('main.index'))
    
    office_id = current_user.office_admin.office_id
    session = CounselingSession.query.filter_by(
        id=session_id, office_id=office_id
    ).first_or_404()
    
    # Get student information
    student = Student.query.get(session.student_id)
    
    # Check if student has any other sessions
    other_sessions = CounselingSession.query.filter(
        CounselingSession.student_id == student.id,
        CounselingSession.id != session_id,
        CounselingSession.office_id == office_id
    ).order_by(desc(CounselingSession.scheduled_at)).limit(5).all()
    
    # Check if student has any inquiries
    student_inquiries = Inquiry.query.filter(
        Inquiry.student_id == student.id,
        Inquiry.office_id == office_id
    ).order_by(desc(Inquiry.created_at)).limit(5).all()
    
    context = get_office_context()
    context.update({
        'session': session,
        'student': student,
        'other_sessions': other_sessions,
        'student_inquiries': student_inquiries
    })
    
    return render_template('office/view_appointment.html', **context)