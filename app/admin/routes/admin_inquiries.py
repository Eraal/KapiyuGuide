from app.models import Inquiry, InquiryMessage, User, Office, db, OfficeAdmin, Student, CounselingSession, StudentActivityLog, SuperAdminActivityLog, OfficeLoginLog, AuditLog
from flask import Blueprint, redirect, url_for, render_template, jsonify, request, flash, Response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, current_user
from flask_socketio import emit
from app import socketio
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from sqlalchemy import func, case, or_, desc
import random
import os
from app.admin import admin_bp

@admin_bp.route('/admin_inquiries')
@login_required
def all_inquiries():
    """
    View all inquiries across offices (Superadmin only)
    This is a read-only view for monitoring purposes
    """
    office_id = request.args.get('office', type=int)
    status = request.args.get('status')
    date_range = request.args.get('date_range')
    search_query = request.args.get('search')
    page = request.args.get('page', 1, type=int)
    per_page = 10

    query = Inquiry.query.join(Student).join(User).join(Office)

    if office_id:
        query = query.filter(Inquiry.office_id == office_id)
    
    if status:
        query = query.filter(Inquiry.status == status)
    
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    if date_range == 'today':
        query = query.filter(Inquiry.created_at >= today)
    elif date_range == 'yesterday':
        yesterday = today - timedelta(days=1)
        query = query.filter(Inquiry.created_at >= yesterday, Inquiry.created_at < today)
    elif date_range == 'this_week':
        start_of_week = today - timedelta(days=today.weekday())
        query = query.filter(Inquiry.created_at >= start_of_week)
    elif date_range == 'last_week':
        start_of_last_week = today - timedelta(days=today.weekday() + 7)
        end_of_last_week = start_of_last_week + timedelta(days=7)
        query = query.filter(Inquiry.created_at >= start_of_last_week, Inquiry.created_at < end_of_last_week)
    elif date_range == 'this_month':
        start_of_month = today.replace(day=1)
        query = query.filter(Inquiry.created_at >= start_of_month)
    elif date_range == 'last_month':
        last_month = today.replace(day=1) - timedelta(days=1)
        start_of_last_month = last_month.replace(day=1)
        query = query.filter(Inquiry.created_at >= start_of_last_month, Inquiry.created_at < today.replace(day=1))
    elif date_range == 'custom':
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(Inquiry.created_at >= start_date)
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)  # Include end date
            query = query.filter(Inquiry.created_at < end_date)
    
    if search_query:
        search = f"%{search_query}%"
        query = query.filter(
            or_(
                User.first_name.ilike(search),
                User.last_name.ilike(search),
                Student.student_number.ilike(search),
                Inquiry.subject.ilike(search),
                Inquiry.content.ilike(search)
            )
        )
    

    offices = Office.query.all()
    
    query = query.order_by(desc(Inquiry.created_at))
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    inquiries = pagination.items

    stats = get_inquiry_stats()
    
    return render_template(
        'admin/all_inquiries.html',
        inquiries=inquiries,
        pagination=pagination,
        offices=offices,
        stats=stats
    )

def get_inquiry_stats():
    """Calculate inquiry statistics for the dashboard"""

    total = Inquiry.query.count()
    pending = Inquiry.query.filter_by(status='pending').count()
    in_progress = Inquiry.query.filter_by(status='in_progress').count()
    resolved = Inquiry.query.filter_by(status='resolved').count()

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_week = today - timedelta(days=today.weekday())
    
    start_of_last_week = start_of_week - timedelta(days=7)
    end_of_last_week = start_of_week - timedelta(seconds=1)
    
    this_week_total = Inquiry.query.filter(Inquiry.created_at >= start_of_week).count()
    
    last_week_total = Inquiry.query.filter(
        Inquiry.created_at >= start_of_last_week,
        Inquiry.created_at <= end_of_last_week
    ).count()

    if last_week_total > 0:
        total_change = ((this_week_total - last_week_total) / last_week_total) * 100
    else:
        total_change = 100 if this_week_total > 0 else 0
    
    this_week_pending = Inquiry.query.filter(
        Inquiry.created_at >= start_of_week,
        Inquiry.status == 'pending'
    ).count()
    
    last_week_pending = Inquiry.query.filter(
        Inquiry.created_at >= start_of_last_week,
        Inquiry.created_at <= end_of_last_week,
        Inquiry.status == 'pending'
    ).count()
    
    if last_week_pending > 0:
        pending_change = ((this_week_pending - last_week_pending) / last_week_pending) * 100
    else:
        pending_change = 100 if this_week_pending > 0 else 0
    
    this_week_in_progress = Inquiry.query.filter(
        Inquiry.created_at >= start_of_week,
        Inquiry.status == 'in_progress'
    ).count()
    
    last_week_in_progress = Inquiry.query.filter(
        Inquiry.created_at >= start_of_last_week,
        Inquiry.created_at <= end_of_last_week,
        Inquiry.status == 'in_progress'
    ).count()
    
    if last_week_in_progress > 0:
        in_progress_change = ((this_week_in_progress - last_week_in_progress) / last_week_in_progress) * 100
    else:
        in_progress_change = 100 if this_week_in_progress > 0 else 0
    
    this_week_resolved = Inquiry.query.filter(
        Inquiry.created_at >= start_of_week,
        Inquiry.status == 'resolved'
    ).count()
    
    last_week_resolved = Inquiry.query.filter(
        Inquiry.created_at >= start_of_last_week,
        Inquiry.created_at <= end_of_last_week,
        Inquiry.status == 'resolved'
    ).count()
    
    if last_week_resolved > 0:
        resolved_change = ((this_week_resolved - last_week_resolved) / last_week_resolved) * 100
    else:
        resolved_change = 100 if this_week_resolved > 0 else 0
    
    # Return all stats
    return {
        'total': total,
        'pending': pending,
        'in_progress': in_progress,
        'resolved': resolved,
        'total_change': round(total_change),
        'pending_change': round(pending_change),
        'in_progress_change': round(in_progress_change),
        'resolved_change': round(resolved_change)
    }

@admin_bp.route('/admin/inquiry/<int:inquiry_id>')
@login_required
def view_inquiry_details(inquiry_id):
    """
    View detailed information about a specific inquiry
    This is for the modal popup when clicking on an inquiry
    """
    inquiry = Inquiry.query.get_or_404(inquiry_id)

    messages = inquiry.messages.order_by(Inquiry.created_at).all() if hasattr(inquiry, 'messages') else []
    
    return render_template(
        'admin/inquiry_details_modal.html',
        inquiry=inquiry,
        messages=messages
    )

@admin_bp.route('/admin/inquiry/export', methods=['POST'])
@login_required
def export_inquiries():
    """
    Export filtered inquiries data in various formats
    """
    export_format = request.form.get('format', 'csv')
    
    office_id = request.form.get('office', type=int)
    status = request.form.get('status')
    date_range = request.form.get('date_range')
    search_query = request.form.get('search')
    
    query = Inquiry.query.join(Student).join(User).join(Office)

    inquiries = query.order_by(desc(Inquiry.created_at)).all()
 
    if export_format == 'csv':
        pass
    elif export_format == 'pdf':
        pass
    elif export_format == 'excel':
        pass
    
    return jsonify({'error': 'Export format not supported'}), 400