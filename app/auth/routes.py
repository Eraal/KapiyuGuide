from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from werkzeug.security import check_password_hash, generate_password_hash  
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, Student, AuditLog
from app.models import User, Student  
from datetime import datetime
from app.extensions import db  
from flask_wtf.csrf import CSRFProtect


auth_bp = Blueprint('auth', __name__, template_folder='../templates') 


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            # Update online status and last activity time
            user.is_online = True
            user.last_activity = datetime.utcnow()
            
            # Successful login
            login_user(user)
            flash('Login successful!', 'success')

            # Log successful login
            log = AuditLog(
                actor_id=user.id,  # Changed from user_id to actor_id
                actor_role=user.role,  # Added actor_role
                action='Logged in',
                target_type='authentication',
                status_snapshot='success',
                is_success=True,
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string if request.user_agent else None
            )
            db.session.add(log)
            db.session.commit()
            
            # Redirect based on role
            if user.role == 'super_admin':
                return redirect(url_for('admin.dashboard')) 
            elif user.role == 'office_admin':
                return redirect(url_for('office.dashboard'))
            elif user.role == 'student':
                return redirect(url_for('student.dashboard'))
            else:
                flash('Unknown user role.', 'danger')
                return redirect(url_for('auth.login'))
        else:
            # Failed login attempt
            log = AuditLog(
                actor_id=user.id if user else None,  # Changed from user_id to actor_id
                actor_role=user.role if user else None,  # Added actor_role
                action='Failed login attempt',
                target_type='authentication',
                status_snapshot='failed',
                is_success=False,
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string if request.user_agent else None,
                failure_reason='Invalid credentials'  # Added failure reason
            )
            db.session.add(log)
            db.session.commit()
            
            flash('Invalid email or password', 'danger')
            return render_template('auth/login.html')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not first_name or not last_name or not email or not password:
            flash('All fields are required', 'error')
            return redirect(url_for('auth.register'))
        
        if not email.endswith('@lspu.edu.ph'):
            flash('Registration is only allowed for LSPU students with @lspu.edu.ph email address', 'error')
            return redirect(url_for('auth.register'))
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists', 'error')
            return redirect(url_for('auth.register'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('auth.register'))
        
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            role='student',  
            password_hash=generate_password_hash(password, method='pbkdf2:sha256'),
            is_active=True
        )
        
        try:
            db.session.add(new_user)
            db.session.flush()  
            
            student = Student(user_id=new_user.id)
            db.session.add(student)
            
            db.session.commit()
            flash('Registration successful! You can now log in', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            print(f"Error during registration: {e}")  
            flash('An error occurred. Please try again.', 'error')
            return redirect(url_for('auth.register'))
    
    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required 
def logout():
    # Update online status before logging out
    current_user.is_online = False
    
    log = AuditLog(
        actor_id=current_user.id,
        actor_role=current_user.role,
        action='Logged out',
        target_type='authentication',
        status_snapshot='success',
        is_success=True,
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string if request.user_agent else None
    )
    db.session.add(log)
    db.session.commit()
    
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))