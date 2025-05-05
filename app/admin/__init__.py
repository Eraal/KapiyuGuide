from flask import Blueprint

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

from .routes import dashboard, adminprofile, student_management, audit_logs
from .routes import office_stats, admin_announcement, admin_inquiries
from .routes import account_settings, add_office, manage_office_admins, edit_office
from .routes import locked_account_history, admin_detail