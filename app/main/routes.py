from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/offices')
def offices():
    return render_template('offices.html')

@main_bp.route('/securityprivacy')
def securityprivacy():
    return render_template('securityprivacy.html')

@main_bp.route('/register')
def register():
    return render_template('auth/register.html')