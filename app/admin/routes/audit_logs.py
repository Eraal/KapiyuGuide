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



################################# AUDIT LOGS ###############################################

@admin_bp.route('/audit-logs')
@login_required
def audit_logs():
    # Get filter parameters
    filter_type = request.args.get('filter_type', 'all')
    search_query = request.args.get('search', '')
    
    # Base queries for different log types
    inquiry_activities = db.session.query(
        Inquiry, User, Office
    ).join(
        Student, Inquiry.student_id == Student.id
    ).join(
        User, Student.user_id == User.id
    ).join(
        Office, Inquiry.office_id == Office.id
    ).order_by(Inquiry.created_at.desc())
    
    # Filter by search query if provided
    if search_query:
        inquiry_activities = inquiry_activities.filter(
            or_(
                User.first_name.ilike(f'%{search_query}%'),
                User.last_name.ilike(f'%{search_query}%'),
                User.email.ilike(f'%{search_query}%'),
                Office.name.ilike(f'%{search_query}%'),
                Inquiry.subject.ilike(f'%{search_query}%')
            )
        )
    
    # Apply filter based on type
    if filter_type == 'student':
        # Get student activity logs
        student_logs = db.session.query(
            StudentActivityLog, Student, User
        ).join(
            Student, StudentActivityLog.student_id == Student.id
        ).join(
            User, Student.user_id == User.id
        ).order_by(StudentActivityLog.timestamp.desc())
        
        if search_query:
            student_logs = student_logs.filter(
                or_(
                    User.first_name.ilike(f'%{search_query}%'),
                    User.last_name.ilike(f'%{search_query}%'),
                    User.email.ilike(f'%{search_query}%'),
                    StudentActivityLog.action.ilike(f'%{search_query}%')
                )
            )
        
        # Get students with inquiry statistics (for summary)
        students = db.session.query(
            User,
            Student,
            func.count(Inquiry.id).label('total_inquiries'),
            func.sum(case((Inquiry.status == 'pending', 1), else_=0)).label('active_inquiries'),
            func.count(CounselingSession.id).label('counseling_sessions')
        ).join(
            Student, User.id == Student.user_id
        ).outerjoin(
            Inquiry, Student.id == Inquiry.student_id
        ).outerjoin(
            CounselingSession, Student.id == CounselingSession.student_id
        ).group_by(
            User.id, Student.id
        ).all()
        
        return render_template('admin/audit_logs.html', 
                              students=students,
                              student_logs=student_logs.all(),
                              filter_type=filter_type,
                              search_query=search_query,
                              view_type='student')
    
    elif filter_type == 'office':
        # Get office login logs
        office_logs = db.session.query(
            OfficeLoginLog, OfficeAdmin, User, Office
        ).join(
            OfficeAdmin, OfficeLoginLog.office_admin_id == OfficeAdmin.id
        ).join(
            User, OfficeAdmin.user_id == User.id
        ).join(
            Office, OfficeAdmin.office_id == Office.id
        ).order_by(OfficeLoginLog.login_time.desc())
        
        if search_query:
            office_logs = office_logs.filter(
                or_(
                    User.first_name.ilike(f'%{search_query}%'),
                    User.last_name.ilike(f'%{search_query}%'),
                    Office.name.ilike(f'%{search_query}%')
                )
            )
        
        # Get office activity statistics (for summary)
        offices = db.session.query(
            Office,
            func.count(Inquiry.id).label('total_inquiries'),
            func.sum(case((Inquiry.status == 'pending', 1), else_=0)).label('pending_inquiries'),
            func.sum(case((Inquiry.status == 'resolved', 1), else_=0)).label('resolved_inquiries'),
            func.count(CounselingSession.id).label('counseling_sessions')
        ).outerjoin(
            Inquiry, Office.id == Inquiry.office_id
        ).outerjoin(
            CounselingSession, Office.id == CounselingSession.office_id
        ).group_by(
            Office.id
        ).all()
        
        return render_template('admin/audit_logs.html', 
                              offices=offices,
                              office_logs=office_logs.all(),
                              filter_type=filter_type,
                              search_query=search_query,
                              view_type='office')
    
    elif filter_type == 'superadmin':
        # Get super admin activity logs
        superadmin_logs = db.session.query(
            SuperAdminActivityLog, User.first_name.label('admin_first_name'),
            User.last_name.label('admin_last_name'),
            User.email.label('admin_email'),
            User.role.label('admin_role')
        ).outerjoin(
            User, SuperAdminActivityLog.super_admin_id == User.id
        ).order_by(SuperAdminActivityLog.timestamp.desc())
        
        if search_query:
            superadmin_logs = superadmin_logs.filter(
                or_(
                    User.first_name.ilike(f'%{search_query}%'),
                    User.last_name.ilike(f'%{search_query}%'),
                    User.email.ilike(f'%{search_query}%'),
                    SuperAdminActivityLog.action.ilike(f'%{search_query}%')
                )
            )
        
        # Get super admin users for summary
        super_admins = db.session.query(
            User,
            func.count(SuperAdminActivityLog.id).label('total_actions')
        ).outerjoin(
            SuperAdminActivityLog, User.id == SuperAdminActivityLog.super_admin_id
        ).filter(
            User.role == 'super_admin'
        ).group_by(
            User.id
        ).all()
        
        return render_template('admin/audit_logs.html', 
                              super_admins=super_admins,
                              superadmin_logs=superadmin_logs.all(),
                              filter_type=filter_type,
                              search_query=search_query,
                              view_type='superadmin')
    
    else:  # 'all' or default view - combined audit logs
        # Get the general audit logs
        audit_logs = db.session.query(
            AuditLog, User
        ).outerjoin(
            User, AuditLog.actor_id == User.id
        ).order_by(AuditLog.timestamp.desc())
        
        if search_query:
            audit_logs = audit_logs.filter(
                or_(
                    User.first_name.ilike(f'%{search_query}%'),
                    User.last_name.ilike(f'%{search_query}%'),
                    User.email.ilike(f'%{search_query}%'),
                    AuditLog.action.ilike(f'%{search_query}%')
                )
            )
        
        page = request.args.get('page', 1, type=int)
        per_page = 20  # or whatever number you prefer
        paginated_logs = audit_logs.paginate(page=page, per_page=per_page, error_out=False)

        return render_template('admin/audit_logs.html', 
                      audit_logs=paginated_logs.items,
                      pagination=paginated_logs,
                      filter_type=filter_type,
                      search_query=search_query,
                      view_type='all')

@admin_bp.route('/export-logs', methods=['GET'])
@login_required
def export_logs():
    """Export logs in various formats."""
    export_format = request.args.get('format', 'csv')
    log_type = request.args.get('type', 'all')
    
    # Get the same logs that would be displayed in the audit_logs view
    # You should reuse the same query logic from your audit_logs function
    logs = get_logs_based_on_type_and_filters(log_type)
    
    if export_format == 'csv':
        return export_logs_csv(logs)
    elif export_format == 'excel':
        return export_logs_excel(logs)
    elif export_format == 'pdf':
        return export_logs_pdf(logs)
    else:
        flash('Unsupported export format', 'error')
        return redirect(url_for('admin.audit_logs', type=log_type))

def get_logs_based_on_type_and_filters(log_type):
    """Get logs based on type and applied filters."""
    # Copy the filtering logic from your audit_logs route
    # This should include handling of all request.args parameters
    
    # Example implementation (adjust according to your data model):
    query = None
    if log_type == 'student':
        query = StudentActivityLog.query
    elif log_type == 'office':
        query = OfficeLoginLog.query
    elif log_type == 'super_admin':
        query = AdminActivityLog.query
    else:  # 'all' or 'audit'
        query = AuditLog.query
    
    # Apply additional filters from request.args
    # Example:
    date_from = request.args.get('date_from')
    if date_from:
        query = query.filter(AuditLog.timestamp >= datetime.strptime(date_from, '%Y-%m-%d'))
    
    date_to = request.args.get('date_to')
    if date_to:
        query = query.filter(AuditLog.timestamp <= datetime.strptime(date_to + ' 23:59:59', '%Y-%m-%d %H:%M:%S'))
    
    # Add more filters based on your request.args and filter needs
    
    return query.all()

def export_logs_csv(logs):
    """Export logs as CSV file."""
    import csv
    from io import StringIO
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['ID', 'User', 'Role', 'Action', 'Related Type', 'Status', 'Timestamp', 'IP Address'])
    
    # Write data rows
    for log in logs:
        writer.writerow([
            log.id,
            log.user_name if hasattr(log, 'user_name') else '',
            log.user_role if hasattr(log, 'user_role') else '',
            log.action,
            log.related_type if hasattr(log, 'related_type') else '',
            'Success' if log.is_success else 'Failed',
            log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            log.ip_address if hasattr(log, 'ip_address') else ''
        ])
    
    output.seek(0)
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename=logs_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
    )

def export_logs_excel(logs):
    """Export logs as Excel file."""
    # You'll need to install openpyxl: pip install openpyxl
    import openpyxl
    from io import BytesIO
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Logs"
    
    # Write header
    ws.append(['ID', 'User', 'Role', 'Action', 'Related Type', 'Status', 'Timestamp', 'IP Address'])
    
    # Write data rows
    for log in logs:
        ws.append([
            log.id,
            log.user_name if hasattr(log, 'user_name') else '',
            log.user_role if hasattr(log, 'user_role') else '',
            log.action,
            log.related_type if hasattr(log, 'related_type') else '',
            'Success' if log.is_success else 'Failed',
            log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            log.ip_address if hasattr(log, 'ip_address') else ''
        ])
    
    # Save to BytesIO
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    return Response(
        output.getvalue(),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-disposition": f"attachment; filename=logs_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"}
    )

def export_logs_pdf(logs):
    """Export logs as PDF file."""
    # You'll need to install reportlab: pip install reportlab
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from io import BytesIO
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Define styles
    styles = getSampleStyleTools()
    title_style = styles['Heading1']
    
    # Add title
    elements.append(Paragraph("Audit Logs Export", title_style))
    
    # Prepare data for table
    data = [['ID', 'User', 'Role', 'Action', 'Related Type', 'Status', 'Timestamp', 'IP Address']]
    
    for log in logs:
        data.append([
            str(log.id),
            log.user_name if hasattr(log, 'user_name') else '',
            log.user_role if hasattr(log, 'user_role') else '',
            log.action,
            log.related_type if hasattr(log, 'related_type') else '',
            'Success' if log.is_success else 'Failed',
            log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            log.ip_address if hasattr(log, 'ip_address') else ''
        ])
    
    # Create table
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    buffer.seek(0)
    
    return Response(
        buffer.getvalue(),
        mimetype="application/pdf",
        headers={"Content-disposition": f"attachment; filename=logs_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"}
    )
