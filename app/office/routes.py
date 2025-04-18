from flask import Blueprint

office_bp = Blueprint('office', __name__, url_prefix='/office')

@office_bp.route('/dashboard')
def dashboard():
    return "Office Admin Dashboard"