from flask import Blueprint, redirect, url_for,render_template
from flask_socketio import emit
from app import socketio
from app.models import Inquiry, InquiryMessage, User, Office, db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
def dashboard():
    office_data = []
    offices = Office.query.all()

    total_students = User.query.filter_by(role='student').count()
    total_office_admins = User.query.filter_by(role='office_admin').count()
    total_inquiries = Inquiry.query.count()
    pending_inquiries = Inquiry.query.filter_by(status='pending').count()
    resolved_inquiries = Inquiry.query.filter_by(status='resolved').count()

    # Example for determining top inquiries (by office with most inquiries)
    top_office = (
        db.session.query(Office.name, db.func.count(Inquiry.id).label('inquiry_count'))
        .join(Inquiry)
        .group_by(Office.id)
        .order_by(db.desc('inquiry_count'))
        .first()
    )
    top_inquiry_office = top_office.name if top_office else "N/A"

    for office in offices:
        inquiry_count = db.session.query(db.func.count(Inquiry.id)).filter(Inquiry.office_id == office.id).scalar()
        office_data.append({
            "name": office.name,
            "count": inquiry_count,
            "bg": "bg-blue-200"  # You can customize this per office if desired
        })

    return render_template(
        'admin/dashboard.html',
        offices=office_data,
        total_students=total_students,
        total_office_admins=total_office_admins,
        total_inquiries=total_inquiries,
        pending_inquiries=pending_inquiries,
        resolved_inquiries=resolved_inquiries,
        top_inquiry_office=top_inquiry_office
    )



@admin_bp.route('/manage-admins')
def manage_admins():
    return "Manage Admins page under construction"

@admin_bp.route('/students')
def students():
    return "Students page under construction"

@admin_bp.route('/inquiry-logs')
def inquiry_logs():
    return "Inquiry Logs page under construction"

@admin_bp.route('/announcement')
def announcement():
    return "Announcement page under construction"