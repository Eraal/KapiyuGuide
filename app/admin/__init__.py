from flask import Blueprint

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

from .routes import dashboard, adminprofile, student_management, audit_logs
from .routes import adminmanagement, admin_announcement, admin_inquiries