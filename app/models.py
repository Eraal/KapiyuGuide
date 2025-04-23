from app.extensions import db
from datetime import datetime
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50))  # optional
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'student', 'office_admin', 'super_admin'
    profile_pic = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('Student', uselist=False, back_populates='user')
    office_admin = db.relationship('OfficeAdmin', uselist=False, back_populates='user')
    notifications = db.relationship('Notification', back_populates='user', lazy=True)
    inquiry_messages = db.relationship('InquiryMessage', back_populates='sender', lazy=True)
    announcements = db.relationship('Announcement', back_populates='author', lazy=True)
    counseling_sessions = db.relationship('CounselingSession', back_populates='counselor', lazy=True)


class Office(db.Model):
    __tablename__ = 'offices'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    supports_video = db.Column(db.Boolean, default=False)

    office_admins = db.relationship('OfficeAdmin', back_populates='office', lazy=True)
    inquiries = db.relationship('Inquiry', back_populates='office', lazy=True)
    counseling_sessions = db.relationship('CounselingSession', back_populates='office', lazy=True)
    announcements = db.relationship('Announcement', back_populates='target_office', lazy=True)


class OfficeAdmin(db.Model):
    __tablename__ = 'office_admins'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    office_id = db.Column(db.Integer, db.ForeignKey('offices.id', ondelete='CASCADE'), nullable=False)

    user = db.relationship('User', back_populates='office_admin')
    office = db.relationship('Office', back_populates='office_admins')


class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    student_number = db.Column(db.String(50))

    user = db.relationship('User', back_populates='student')
    inquiries = db.relationship('Inquiry', back_populates='student', lazy=True)
    counseling_sessions = db.relationship('CounselingSession', back_populates='student', lazy=True)


class Inquiry(db.Model):
    __tablename__ = 'inquiries'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    office_id = db.Column(db.Integer, db.ForeignKey('offices.id', ondelete='CASCADE'), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('Student', back_populates='inquiries')
    office = db.relationship('Office', back_populates='inquiries')
    messages = db.relationship('InquiryMessage', back_populates='inquiry', lazy=True)


class InquiryMessage(db.Model):
    __tablename__ = 'inquiry_messages'
    id = db.Column(db.Integer, primary_key=True)
    inquiry_id = db.Column(db.Integer, db.ForeignKey('inquiries.id', ondelete='CASCADE'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='sent')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    delivered_at = db.Column(db.DateTime)  # Optional: timestamp when message was delivered
    read_at = db.Column(db.DateTime)       # Optional: timestamp when message was read

    inquiry = db.relationship('Inquiry', back_populates='messages')
    sender = db.relationship('User', back_populates='inquiry_messages')


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='notifications')


class CounselingSession(db.Model):
    __tablename__ = 'counseling_sessions'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    office_id = db.Column(db.Integer, db.ForeignKey('offices.id', ondelete='CASCADE'), nullable=False)
    counselor_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    scheduled_at = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), default='pending')
    notes = db.Column(db.Text)

    student = db.relationship('Student', back_populates='counseling_sessions')
    office = db.relationship('Office', back_populates='counseling_sessions')
    counselor = db.relationship('User', back_populates='counseling_sessions')


class Announcement(db.Model):
    __tablename__ = 'announcements'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    target_office_id = db.Column(db.Integer, db.ForeignKey('offices.id', ondelete='SET NULL'))
    is_public = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    author = db.relationship('User', back_populates='announcements')
    target_office = db.relationship('Office', back_populates='announcements')
