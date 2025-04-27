from app.extensions import db
from datetime import datetime
from flask_login import UserMixin

class JsonSerializableMixin:
    """Mixin to make models JSON serializable"""
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50))  # optional
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, index=True)  # 'student', 'office_admin', 'super_admin'
    profile_pic = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    student = db.relationship('Student', uselist=False, back_populates='user')
    office_admin = db.relationship('OfficeAdmin', uselist=False, back_populates='user')
    notifications = db.relationship('Notification', back_populates='user', lazy=True)
    inquiry_messages = db.relationship('InquiryMessage', back_populates='sender', lazy=True)
    announcements = db.relationship('Announcement', back_populates='author', lazy=True)
    counseling_sessions = db.relationship('CounselingSession', back_populates='counselor', lazy=True)

    def get_full_name(self):
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"

class Office(db.Model):
    __tablename__ = 'offices'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text)
    supports_video = db.Column(db.Boolean, default=False)
    office_admins = db.relationship('OfficeAdmin', back_populates='office', lazy=True)
    inquiries = db.relationship('Inquiry', back_populates='office', lazy=True)
    counseling_sessions = db.relationship('CounselingSession', back_populates='office', lazy=True)
    announcements = db.relationship('Announcement', back_populates='target_office', lazy=True)

class OfficeAdmin(db.Model):
    __tablename__ = 'office_admins'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    office_id = db.Column(db.Integer, db.ForeignKey('offices.id', ondelete='CASCADE'), nullable=False, index=True)

    user = db.relationship('User', back_populates='office_admin')
    office = db.relationship('Office', back_populates='office_admins')

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    student_number = db.Column(db.String(50), index=True)

    user = db.relationship('User', back_populates='student')
    inquiries = db.relationship('Inquiry', back_populates='student', lazy=True)
    counseling_sessions = db.relationship('CounselingSession', back_populates='student', lazy=True)


class Inquiry(db.Model):
    __tablename__ = 'inquiries'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False, index=True)
    office_id = db.Column(db.Integer, db.ForeignKey('offices.id', ondelete='CASCADE'), nullable=False, index=True)
    subject = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), default='pending', index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    student = db.relationship('Student', back_populates='inquiries')
    office = db.relationship('Office', back_populates='inquiries')
    messages = db.relationship('InquiryMessage', back_populates='inquiry', lazy=True)


class InquiryMessage(db.Model):
    __tablename__ = 'inquiry_messages'
    id = db.Column(db.Integer, primary_key=True)
    inquiry_id = db.Column(db.Integer, db.ForeignKey('inquiries.id', ondelete='CASCADE'), nullable=False, index=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='sent', index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    delivered_at = db.Column(db.DateTime)  # Optional: timestamp when message was delivered
    read_at = db.Column(db.DateTime)       # Optional: timestamp when message was read

    inquiry = db.relationship('Inquiry', back_populates='messages')
    sender = db.relationship('User', back_populates='inquiry_messages')


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    user = db.relationship('User', back_populates='notifications')


class CounselingSession(db.Model):
    __tablename__ = 'counseling_sessions'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False, index=True)
    office_id = db.Column(db.Integer, db.ForeignKey('offices.id', ondelete='CASCADE'), nullable=False, index=True)
    counselor_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    scheduled_at = db.Column(db.DateTime, nullable=False, index=True)
    status = db.Column(db.String(50), default='pending', index=True)
    notes = db.Column(db.Text)

    student = db.relationship('Student', back_populates='counseling_sessions')
    office = db.relationship('Office', back_populates='counseling_sessions')
    counselor = db.relationship('User', back_populates='counseling_sessions')


class Announcement(db.Model):
    __tablename__ = 'announcements'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    target_office_id = db.Column(db.Integer, db.ForeignKey('offices.id', ondelete='SET NULL'), index=True)
    is_public = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    author = db.relationship('User', back_populates='announcements')
    target_office = db.relationship('Office', back_populates='announcements')
    images = db.relationship('AnnouncementImage', back_populates='announcement', lazy=True, cascade='all, delete-orphan')

class AnnouncementImage(db.Model):
    __tablename__ = 'announcement_images'
    id = db.Column(db.Integer, primary_key=True)
    announcement_id = db.Column(db.Integer, db.ForeignKey('announcements.id', ondelete='CASCADE'), nullable=False, index=True)
    image_path = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(255))
    display_order = db.Column(db.Integer, default=0)  # For ordering images
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    announcement = db.relationship('Announcement', back_populates='images')

# Audit log to track all actions by users (students, office admins, super admins all does they do in system)
class AuditLog(db.Model, JsonSerializableMixin):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), index=True)
    actor_role = db.Column(db.String(20), index=True)  # 'student', 'office_admin', 'super_admin'
    action = db.Column(db.String(100), nullable=False, index=True)  # 'Submitted', 'Replied', etc.
    target_type = db.Column(db.String(50), index=True)  # 'user', 'office', 'inquiry', 'counseling_session', etc.
    inquiry_id = db.Column(db.Integer, db.ForeignKey('inquiries.id', ondelete='SET NULL'), index=True)
    office_id = db.Column(db.Integer, db.ForeignKey('offices.id', ondelete='SET NULL'), index=True)
    status_snapshot = db.Column(db.String(50))
    is_success = db.Column(db.Boolean, default=True)
    failure_reason = db.Column(db.String(255))
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    retention_days = db.Column(db.Integer, default=365)  # Keep logs for 1 year by default

    actor = db.relationship('User')
    inquiry = db.relationship('Inquiry')
    office = db.relationship('Office')

    @classmethod
    def log_action(cls, actor, action, target_type=None, inquiry=None, office=None, status=None, is_success=True, 
                  failure_reason=None, ip_address=None, user_agent=None, retention_days=365):
        """Helper method to create a new audit log entry"""
        log = cls(
            actor_id=actor.id if actor else None,
            actor_role=actor.role if actor else None,
            action=action,
            target_type=target_type,
            inquiry_id=inquiry.id if inquiry else None,
            office_id=office.id if office else None,
            status_snapshot=status,
            is_success=is_success,
            failure_reason=failure_reason,
            ip_address=ip_address,
            user_agent=user_agent,
            retention_days=retention_days
        )
        db.session.add(log)
        return log


# Student activity log for tracking actions performed by students
class StudentActivityLog(db.Model, JsonSerializableMixin):
    __tablename__ = 'student_activity_logs'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), index=True)
    action = db.Column(db.String(100), nullable=False, index=True)  # e.g. 'Requested Counseling'
    related_id = db.Column(db.Integer, index=True)
    related_type = db.Column(db.String(50), index=True)  # 'inquiry', 'counseling'
    is_success = db.Column(db.Boolean, default=True)
    failure_reason = db.Column(db.String(255))
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    retention_days = db.Column(db.Integer, default=365)  # Keep logs for 1 year by default

    student = db.relationship('Student')

    @classmethod
    def log_action(cls, student, action, related_id=None, related_type=None, is_success=True, 
                  failure_reason=None, ip_address=None, user_agent=None, retention_days=365):
        """Helper method to create a new student activity log entry"""
        log = cls(
            student_id=student.id,
            action=action,
            related_id=related_id,
            related_type=related_type,
            is_success=is_success,
            failure_reason=failure_reason,
            ip_address=ip_address,
            user_agent=user_agent,
            retention_days=retention_days
        )
        db.session.add(log)
        return log

# Office login logs to track the time when office admins log in
class OfficeLoginLog(db.Model, JsonSerializableMixin):
    __tablename__ = 'office_login_logs'
    id = db.Column(db.Integer, primary_key=True)
    office_admin_id = db.Column(db.Integer, db.ForeignKey('office_admins.id', ondelete='CASCADE'), index=True)
    login_time = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    logout_time = db.Column(db.DateTime)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    session_duration = db.Column(db.Integer)  # Duration in seconds
    is_success = db.Column(db.Boolean, default=True)
    failure_reason = db.Column(db.String(255))
    retention_days = db.Column(db.Integer, default=365)  # Keep logs for 1 year by default

    office_admin = db.relationship('OfficeAdmin')

    @classmethod
    def log_login(cls, office_admin, ip_address=None, user_agent=None, is_success=True,
                failure_reason=None, retention_days=365):
        """Helper method to create a new office login log entry"""
        log = cls(
            office_admin_id=office_admin.id,
            ip_address=ip_address,
            user_agent=user_agent,
            is_success=is_success,
            failure_reason=failure_reason,
            retention_days=retention_days
        )
        db.session.add(log)
        return log

    def update_logout(self, logout_time=None):
        """Update the logout time and calculate session duration"""
        self.logout_time = logout_time or datetime.utcnow()
        if self.login_time:
            # Calculate session duration in seconds
            self.session_duration = (self.logout_time - self.login_time).total_seconds()


# Super admin activity log to track super admin actions
class SuperAdminActivityLog(db.Model, JsonSerializableMixin):
    __tablename__ = 'super_admin_activity_logs'
    id = db.Column(db.Integer, primary_key=True)
    super_admin_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), index=True)
    action = db.Column(db.String(100), nullable=False, index=True)  # e.g. 'Activated Student', 'Reset Password'
    target_type = db.Column(db.String(50), index=True)  # 'user', 'office', 'system', etc.
    target_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), index=True)
    target_office_id = db.Column(db.Integer, db.ForeignKey('offices.id', ondelete='SET NULL'), index=True)
    details = db.Column(db.Text)  # Optional: more details
    is_success = db.Column(db.Boolean, default=True)
    failure_reason = db.Column(db.String(255))
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    retention_days = db.Column(db.Integer, default=730)  # Super admin logs kept longer by default (2 years)

    super_admin = db.relationship('User', foreign_keys=[super_admin_id])
    target_user = db.relationship('User', foreign_keys=[target_user_id])
    target_office = db.relationship('Office')

    @classmethod
    def log_action(cls, super_admin, action, target_type=None, target_user=None, target_office=None, 
                  details=None, is_success=True, failure_reason=None, ip_address=None, 
                  user_agent=None, retention_days=730):
        """Helper method to create a new super admin activity log entry"""
        log = cls(
            super_admin_id=super_admin.id,
            action=action,
            target_type=target_type,
            target_user_id=target_user.id if target_user else None,
            target_office_id=target_office.id if target_office else None,
            details=details,
            is_success=is_success,
            failure_reason=failure_reason,
            ip_address=ip_address,
            user_agent=user_agent,
            retention_days=retention_days
        )
        db.session.add(log)
        return log