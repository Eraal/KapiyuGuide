from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from werkzeug.security import check_password_hash, generate_password_hash  # Added import
from app.extensions import db  
from app.models import User, Student  # Added Student import

auth_bp = Blueprint('auth', __name__, template_folder='../templates') 

print(generate_password_hash('admin', method='pbkdf2:sha256'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form data
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Find the user
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['role'] = user.role
            flash('Login successful!', 'success')

            # Fixed redirects - use blueprint prefixes
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
            flash('Invalid email or password', 'danger')
            return render_template('auth/login.html')
    
    # For GET requests, just render the login form
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
        
        # Basic validation
        if not first_name or not last_name or not email or not password:
            flash('All fields are required', 'danger')
            return render_template('auth/register.html')  # Fixed path
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('auth/register.html')  # Fixed path
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered', 'danger')
            return render_template('auth/register.html')  # Fixed path
        
        # Create new user
        try:
            # Create user record
            new_user = User(
                name=f"{first_name} {last_name}",
                email=email,
                password_hash=generate_password_hash(password),
                role='student'  # Default role for registration
            )
            
            db.session.add(new_user)
            db.session.flush()  # This gets the ID for the new user
            
           
            new_student = Student(
                user_id=new_user.id,
                student_number=None  
            )
            
            db.session.add(new_student)
            db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred during registration: {str(e)}', 'danger')
            return render_template('auth/register.html')  # Fixed path
    
    # For GET requests, render the registration form
    return render_template('auth/register.html')  # Fixed path