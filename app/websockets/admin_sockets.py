from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from app.models import (
    User, Inquiry, CounselingSession, AuditLog, Office, 
    Notification, OfficeAdmin, Student, SuperAdminActivityLog,
    OfficeLoginLog, StudentActivityLog
)
from app.extensions import db, socketio
from datetime import datetime
import json

def init_socketio():
    """Register admin socket event handlers"""
    register_connection_handlers()
    register_inquiry_handlers()
    register_session_handlers()
    register_system_log_handlers()
    register_announcement_handlers()
    register_user_management_handlers()
    register_office_management_handlers()
    register_super_admin_handlers()
    register_dashboard_handlers()

def register_connection_handlers():
    @socketio.on('connect')
    def handle_connect():
        if not current_user.is_authenticated:
            print(f"Unauthenticated connection attempt rejected")
            return False

        if current_user.role in ['office_admin', 'super_admin']:

            join_room('admin_room')
            join_room(f"user_{current_user.id}")
            
            # Super admin joins special room for super admin only broadcasts
            if current_user.role == 'super_admin':
                join_room('admin_room')
                print(f"Super Admin {current_user.email} joined admin_room")
            
            print(f"Admin {current_user.email} joined admin_room")
            
            if current_user.role == 'super_admin':
                SuperAdminActivityLog.log_action(
                    super_admin=current_user,
                    action="WebSocket Connect",
                    target_type="system",
                    details="Super admin real-time dashboard connection"
                )
            else:
                AuditLog.log_action(
                    actor=current_user,
                    action="WebSocket Connect",
                    target_type="system"
                )
            db.session.commit()
            
            emit('connection_success', {
                'status': 'connected', 
                'user': current_user.email,
                'role': current_user.role
            })
    
    @socketio.on('disconnect')
    def handle_disconnect():
        if current_user.is_authenticated:
            if current_user.role in ['office_admin', 'super_admin']:
                leave_room('admin_room')
                leave_room(f"user_{current_user.id}")
                
                if current_user.role == 'super_admin':
                    leave_room('admin_room')
                    SuperAdminActivityLog.log_action(
                        super_admin=current_user,
                        action="WebSocket Disconnect",
                        target_type="system",
                        details="Super admin real-time dashboard disconnection"
                    )
                else:
                    AuditLog.log_action(
                        actor=current_user,
                        action="WebSocket Disconnect",
                        target_type="system"
                    )
                db.session.commit()

def register_inquiry_handlers():
    @socketio.on('join_admin_room')
    def handle_join_admin_room(data=None):
        if current_user.is_authenticated and current_user.role in ['super_admin', 'office_admin']:
            join_room('admin_room')
            print(f"Admin {current_user.email} joined admin_room")
            emit('connection_success', {
                'status': 'connected', 
                'user': current_user.email,
                'role': current_user.role
            })
    
    @socketio.on('new_inquiry_created')
    def handle_new_inquiry(data):
        emit('new_inquiry', {
            'student_name': data.get('student_name', 'Unknown Student'),
            'subject': data.get('subject', 'New Inquiry'),
            'office_id': data.get('office_id'),
            'office_name': data.get('office_name', 'Unknown Office'),
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }, room='admin_room')

    @socketio.on('inquiry_resolved')
    def handle_inquiry_resolved(data):
        emit('resolved_inquiry', {
            'admin_name': data.get('admin_name', current_user.first_name if current_user.is_authenticated else 'Unknown Admin'),
            'inquiry_id': data.get('inquiry_id'),
            'office_id': data.get('office_id'),
            'office_name': data.get('office_name', 'Unknown Office'),
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }, room='admin_room')

def register_session_handlers():
    @socketio.on('counseling_session_created')
    def handle_new_session(data):
        emit('new_session', {
            'student_name': data.get('student_name', 'Unknown Student'),
            'office_name': data.get('office_name', 'Unknown Office'),
            'office_id': data.get('office_id'),
            'counselor_name': data.get('counselor_name', 'Unassigned'),
            'scheduled_at': data.get('scheduled_at'),
            'session_id': data.get('session_id'),
            'status': data.get('status', 'scheduled')
        }, room='admin_room')
    
    @socketio.on('counseling_session_updated')
    def handle_session_update(data):
        emit('session_update', {
            'session_id': data.get('session_id'),
            'student_name': data.get('student_name', 'Unknown Student'),
            'office_name': data.get('office_name', 'Unknown Office'),
            'counselor_name': data.get('counselor_name', 'Unassigned'),
            'scheduled_at': data.get('scheduled_at'),
            'status': data.get('status', 'updated'),
            'updated_by': data.get('updated_by', current_user.get_full_name() if current_user.is_authenticated else 'System'),
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }, room='admin_room')

def register_system_log_handlers():
    @socketio.on('system_log_created')
    def handle_system_log(data):
        emit('system_log', {
            'action': data.get('action', 'System Event'),
            'actor': {
                'name': data.get('actor_name', 'System'),
                'role': data.get('actor_role', 'system')
            },
            'target_type': data.get('target_type', 'system'),
            'is_success': data.get('is_success', True),
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }, room='admin_room')

def register_announcement_handlers():
    @socketio.on('admin_announcement_created')
    def handle_new_announcement(data):
        """Broadcast when a new announcement is created"""
        emit('new_announcement', data, room='admin_room')

        # Create notifications for relevant users
        if data.get('is_public', False):
            users = User.query.filter(User.is_active == True).all()
        else:
            office_id = data.get('target_office_id')
            users = User.query.join(OfficeAdmin).filter(
                OfficeAdmin.office_id == office_id,
                User.is_active == True
            ).all()

        for user in users:
            notification = Notification(
                user_id=user.id,
                title="New Announcement",
                message=f"New announcement: {data.get('title')}",
                is_read=False
            )
            db.session.add(notification)

        db.session.commit()

def register_user_management_handlers():
    """Register handlers for user management events"""
    
    @socketio.on('user_created')
    def handle_new_user(data):
        """Broadcast when a new user is created"""
        emit('new_user', {
            'user_id': data.get('user_id'),
            'name': data.get('name', 'New User'),
            'email': data.get('email', ''),
            'role': data.get('role', 'student'),
            'created_by': data.get('created_by', current_user.get_full_name() if current_user.is_authenticated else 'System'),
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }, room='admin_room')
    
    @socketio.on('user_updated')
    def handle_user_update(data):
        """Broadcast when a user's details are updated"""
        emit('user_update', {
            'user_id': data.get('user_id'),
            'name': data.get('name', 'Unknown User'),
            'field_updated': data.get('field_updated', 'details'),
            'new_value': data.get('new_value', ''),
            'updated_by': data.get('updated_by', current_user.get_full_name() if current_user.is_authenticated else 'System'),
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }, room='admin_room')
    
    @socketio.on('user_status_changed')
    def handle_user_status_change(data):
        """Broadcast when a user's status changes (activated, deactivated)"""
        emit('user_status_change', {
            'user_id': data.get('user_id'),
            'name': data.get('name', 'Unknown User'),
            'status': data.get('status', 'unknown'),
            'changed_by': data.get('changed_by', current_user.get_full_name() if current_user.is_authenticated else 'System'),
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }, room='admin_room')

def register_office_management_handlers():
    """Register handlers for office management events"""
    
    @socketio.on('office_created')
    def handle_new_office(data):
        """Broadcast when a new office is created"""
        emit('new_office', {
            'office_id': data.get('office_id'),
            'name': data.get('name', 'New Office'),
            'description': data.get('description', ''),
            'created_by': data.get('created_by', current_user.get_full_name() if current_user.is_authenticated else 'System'),
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }, room='admin_room')
    
    @socketio.on('office_updated')
    def handle_office_update(data):
        """Broadcast when an office's details are updated"""
        emit('office_update', {
            'office_id': data.get('office_id'),
            'name': data.get('name', 'Unknown Office'),
            'field_updated': data.get('field_updated', 'details'),
            'new_value': data.get('new_value', ''),
            'updated_by': data.get('updated_by', current_user.get_full_name() if current_user.is_authenticated else 'System'),
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }, room='admin_room')
    
    @socketio.on('admin_assigned_to_office')
    def handle_admin_office_assignment(data):
        """Broadcast when an admin is assigned to an office"""
        emit('admin_office_assignment', {
            'admin_id': data.get('admin_id'),
            'admin_name': data.get('admin_name', 'Unknown Admin'),
            'office_id': data.get('office_id'),
            'office_name': data.get('office_name', 'Unknown Office'),
            'assigned_by': data.get('assigned_by', current_user.get_full_name() if current_user.is_authenticated else 'System'),
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }, room='admin_room')

def register_super_admin_handlers():
    """Register handlers specific to super admin activities"""
    
    @socketio.on('super_admin_action')
    def handle_super_admin_action(data):
        """Broadcast super admin specific actions"""
        emit('super_admin_activity', {
            'admin_id': data.get('admin_id', current_user.id if current_user.is_authenticated else None),
            'admin_name': data.get('admin_name', current_user.get_full_name() if current_user.is_authenticated else 'Unknown Admin'),
            'action': data.get('action', 'Unknown Action'),
            'target_type': data.get('target_type', 'system'),
            'target_id': data.get('target_id'),
            'details': data.get('details', ''),
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }, room='admin_room')
    
    @socketio.on('join_super_admin_room')
    def handle_join_super_admin_room():
        """Allow a super admin to join the super admin room"""
        if current_user.is_authenticated and current_user.role == 'super_admin':
            join_room('admin_room')
            print(f"Super Admin {current_user.email} joined admin_room")
            emit('super_admin_connection', {
                'status': 'connected', 
                'user': current_user.email
            })

def register_dashboard_handlers():
    """Register handlers for dashboard statistics and analytics"""
    
    @socketio.on('request_dashboard_stats')
    def handle_dashboard_stats_request():
        """Handle request for dashboard statistics"""
        if not current_user.is_authenticated or current_user.role != 'super_admin':
            return
        
        # Get real-time statistics
        active_users = User.query.filter_by(is_active=True).count()
        pending_inquiries = Inquiry.query.filter_by(status='pending').count()
        upcoming_sessions = CounselingSession.query.filter(
            CounselingSession.scheduled_at > datetime.utcnow(),
            CounselingSession.status == 'scheduled'
        ).count()
        
        # Get office activity
        offices = Office.query.all()
        office_activity = []
        for office in offices:
            inquiries_count = Inquiry.query.filter_by(office_id=office.id).count()
            sessions_count = CounselingSession.query.filter_by(office_id=office.id).count()
            office_activity.append({
                'office_id': office.id,
                'office_name': office.name,
                'inquiries_count': inquiries_count,
                'sessions_count': sessions_count
            })
        
        emit('dashboard_stats', {
            'active_users': active_users,
            'pending_inquiries': pending_inquiries,
            'upcoming_sessions': upcoming_sessions,
            'office_activity': office_activity,
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    @socketio.on('request_system_health')
    def handle_system_health_request():
        """Handle request for system health metrics"""
        if not current_user.is_authenticated or current_user.role != 'super_admin':
            return
            
        # Get recent audit logs for system health overview
        recent_logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(20).all()
        log_data = []
        for log in recent_logs:
            log_data.append({
                'action': log.action,
                'actor_role': log.actor_role,
                'target_type': log.target_type,
                'is_success': log.is_success,
                'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        # Get user login statistics
        office_logins = OfficeLoginLog.query.filter(
            OfficeLoginLog.login_time > datetime.utcnow().replace(hour=0, minute=0, second=0)
        ).count()
        
        # Get daily student activity count
        student_activity = StudentActivityLog.query.filter(
            StudentActivityLog.timestamp > datetime.utcnow().replace(hour=0, minute=0, second=0)
        ).count()
        
        emit('system_health', {
            'recent_logs': log_data,
            'daily_office_logins': office_logins,
            'daily_student_activity': student_activity,
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        })

# Utility functions for emitting events from other parts of the application
def emit_inquiry_update(inquiry, action_type):
    """
    Emit WebSocket event for inquiry updates.
    
    :param inquiry: The inquiry object
    :param action_type: 'new' or 'resolved'
    """
    if action_type == 'new':
        student = User.query.join(Student).filter(Student.id == inquiry.student_id).first()
        student_name = student.get_full_name() if student else "Unknown Student"
        
        office = Office.query.get(inquiry.office_id)
        office_name = office.name if office else "Unknown Office"
        
        socketio.emit('new_inquiry', {
            'inquiry_id': inquiry.id,
            'student_name': student_name,
            'subject': inquiry.subject,
            'office_id': inquiry.office_id,
            'office_name': office_name,
            'timestamp': inquiry.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }, room='admin_room')
    
    elif action_type == 'resolved':
        # Assuming resolved_by is a field in your Inquiry model
        admin = User.query.get(inquiry.resolved_by) if hasattr(inquiry, 'resolved_by') and inquiry.resolved_by else None
        admin_name = admin.get_full_name() if admin else "Unknown Admin"
        
        office = Office.query.get(inquiry.office_id)
        office_name = office.name if office else "Unknown Office"
        
        socketio.emit('resolved_inquiry', {
            'inquiry_id': inquiry.id,
            'admin_name': admin_name,
            'office_id': inquiry.office_id,
            'office_name': office_name,
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }, room='admin_room')

def emit_system_log(log):
    """
    Emit WebSocket event for system logs.
    
    :param log: The AuditLog object
    """
    actor = None
    actor_name = "System"
    actor_role = "system"
    
    if hasattr(log, 'actor_id') and log.actor_id:
        actor = User.query.get(log.actor_id)
        if actor:
            actor_name = f"{actor.first_name} {actor.last_name}"
            actor_role = actor.role
    
    socketio.emit('system_log', {
        'action': log.action,
        'actor': {
            'name': actor_name,
            'role': actor_role
        },
        'target_type': log.target_type if hasattr(log, 'target_type') else 'system',
        'is_success': log.is_success if hasattr(log, 'is_success') else True,
        'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    }, room='admin_room')

def emit_session_update(session, action_type):
    """
    Emit WebSocket event for counseling session updates.
    
    :param session: The CounselingSession object
    :param action_type: 'new', 'updated', 'cancelled', 'completed'
    """
    student = User.query.join(Student).filter(Student.id == session.student_id).first()
    student_name = student.get_full_name() if student else "Unknown Student"
    
    office = Office.query.get(session.office_id)
    office_name = office.name if office else "Unknown Office"
    
    counselor = User.query.get(session.counselor_id)
    counselor_name = counselor.get_full_name() if counselor else "Unassigned"
    
    event_data = {
        'session_id': session.id,
        'student_name': student_name,
        'office_name': office_name,
        'office_id': session.office_id,
        'counselor_name': counselor_name,
        'scheduled_at': session.scheduled_at.strftime('%Y-%m-%d %H:%M:%S'),
        'status': session.status,
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    if action_type == 'new':
        socketio.emit('new_session', event_data, room='admin_room')
    else:
        event_data['action_type'] = action_type
        socketio.emit('session_update', event_data, room='admin_room')

def emit_user_update(user, action_type, updated_by=None, field_updated=None, new_value=None):
    """
    Emit WebSocket event for user updates.
    
    :param user: The User object
    :param action_type: 'created', 'updated', 'status_changed'
    :param updated_by: User who made the update
    :param field_updated: Field that was updated (for 'updated' action_type)
    :param new_value: New value of the updated field
    """
    user_data = {
        'user_id': user.id,
        'name': user.get_full_name(),
        'email': user.email,
        'role': user.role,
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    if updated_by:
        user_data['updated_by'] = updated_by.get_full_name() if hasattr(updated_by, 'get_full_name') else str(updated_by)
    
    if action_type == 'created':
        socketio.emit('new_user', user_data, room='admin_room')
    
    elif action_type == 'updated':
        user_data['field_updated'] = field_updated
        user_data['new_value'] = new_value
        socketio.emit('user_update', user_data, room='admin_room')
    
    elif action_type == 'status_changed':
        user_data['status'] = 'active' if user.is_active else 'inactive'
        socketio.emit('user_status_change', user_data, room='admin_room')

def emit_office_update(office, action_type, updated_by=None, field_updated=None, new_value=None):
    """
    Emit WebSocket event for office updates.
    
    :param office: The Office object
    :param action_type: 'created', 'updated'
    :param updated_by: User who made the update
    :param field_updated: Field that was updated (for 'updated' action_type)
    :param new_value: New value of the updated field
    """
    office_data = {
        'office_id': office.id,
        'name': office.name,
        'description': office.description,
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    if updated_by:
        office_data['updated_by'] = updated_by.get_full_name() if hasattr(updated_by, 'get_full_name') else str(updated_by)
    
    if action_type == 'created':
        socketio.emit('new_office', office_data, room='admin_room')
    
    elif action_type == 'updated':
        office_data['field_updated'] = field_updated
        office_data['new_value'] = new_value
        socketio.emit('office_update', office_data, room='admin_room')

def emit_super_admin_activity(admin, action, target_type, target=None, details=None):
    """
    Emit WebSocket event for super admin activities.
    
    :param admin: The admin User object
    :param action: Description of the action
    :param target_type: Type of target (user, office, system, etc.)
    :param target: Target object
    :param details: Additional details
    """
    activity_data = {
        'admin_id': admin.id,
        'admin_name': admin.get_full_name(),
        'action': action,
        'target_type': target_type,
        'details': details or '',
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    if target:
        activity_data['target_id'] = target.id if hasattr(target, 'id') else None
        if hasattr(target, 'get_full_name'):
            activity_data['target_name'] = target.get_full_name()
        elif hasattr(target, 'name'):
            activity_data['target_name'] = target.name
    
    socketio.emit('super_admin_activity', activity_data, room='admin_room')

def update_dashboard_stats():
    """
    Update real-time dashboard statistics for super admins.
    This can be called periodically or after significant system events.
    """
    active_users = User.query.filter_by(is_active=True).count()
    pending_inquiries = Inquiry.query.filter_by(status='pending').count()
    upcoming_sessions = CounselingSession.query.filter(
        CounselingSession.scheduled_at > datetime.utcnow(),
        CounselingSession.status == 'scheduled'
    ).count()
    
    offices = Office.query.all()
    office_activity = []
    for office in offices:
        inquiries_count = Inquiry.query.filter_by(office_id=office.id).count()
        sessions_count = CounselingSession.query.filter_by(office_id=office.id).count()
        office_activity.append({
            'office_id': office.id,
            'office_name': office.name,
            'inquiries_count': inquiries_count,
            'sessions_count': sessions_count
        })
    
    socketio.emit('dashboard_stats', {
        'active_users': active_users,
        'pending_inquiries': pending_inquiries,
        'upcoming_sessions': upcoming_sessions,
        'office_activity': office_activity,
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    }, room='admin_room')