from flask import Blueprint


admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

from .routes.dashboard import *
from .routes.adminprofile import *
from .routes.student_management import *
from .routes.audit_logs import *
from .routes.adminmanagement import *
from .routes.admin_announcement import *