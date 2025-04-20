from flask import Blueprint, redirect, url_for, render_template, jsonify, request, flash
from flask_socketio import emit
from app import socketio
from app.models import Inquiry, InquiryMessage, User, Office, db, OfficeAdmin
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from datetime import datetime
import os

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

################################ PROFILE MANAGEMENT ###################################################################

@admin_bp.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    if not current_user.role == 'office_admin' and not current_user.role == 'super_admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        # Get form data
        first_name = request.form.get('first_name')
        middle_name = request.form.get('middle_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        
        # Validate required fields
        if not first_name or not last_name or not email:
            flash('Please fill all required fields', 'error')
            return redirect(url_for('admin.dashboard'))
        
        # Check if email is already in use (if changed)
        if email != current_user.email:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('Email address is already in use', 'error')
                return redirect(url_for('admin.dashboard'))
        
        # Update user data
        current_user.first_name = first_name
        current_user.middle_name = middle_name
        current_user.last_name = last_name
        current_user.email = email
        
        db.session.commit()
        flash('Profile updated successfully', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating profile: {str(e)}', 'error')
    
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/update_profile_photo', methods=['POST'])
@login_required
def update_profile_photo():
    if not current_user.role == 'office_admin' and not current_user.role == 'super_admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        if 'profile_photo' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(url_for('admin.dashboard'))
        
        file = request.files['profile_photo']
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('admin.dashboard'))
        
        if file:
            # Define allowed file extensions
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
            if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
                flash('Invalid file format. Please upload a JPG, PNG, or GIF file.', 'error')
                return redirect(url_for('admin.dashboard'))
            
            # Create upload directory if it doesn't exist
            upload_dir = os.path.join('app', 'static', 'uploads', 'profile_pics')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Create unique filename
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"user_{current_user.id}_{timestamp}_{secure_filename(file.filename)}"
            filepath = os.path.join(upload_dir, filename)
            
            # Save the file
            file.save(filepath)
            

            db_filepath = os.path.join('uploads', 'profile_pics', filename)
            
            # Delete old profile pic if exists
            if current_user.profile_pic:
                old_file_path = os.path.join('app', 'static', current_user.profile_pic)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
            
            current_user.profile_pic = db_filepath
            db.session.commit()
            
            flash('Profile photo updated successfully', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating profile photo: {str(e)}', 'error')
    
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/remove_profile_photo', methods=['POST'])
@login_required
def remove_profile_photo():
    if not current_user.role == 'office_admin' and not current_user.role == 'super_admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        if current_user.profile_pic:
            file_path = os.path.join('app', 'static', current_user.profile_pic)
            if os.path.exists(file_path):
                os.remove(file_path)
            
            current_user.profile_pic = None
            db.session.commit()
            
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'No profile photo to remove'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@admin_bp.route('/change_password', methods=['POST'])
@login_required
def change_password():
    if not current_user.role == 'office_admin' and not current_user.role == 'super_admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_new_password = request.form.get('confirm_new_password')
        
        # Validate passwords
        if not current_password or not new_password or not confirm_new_password:
            flash('All password fields are required', 'error')
            return redirect(url_for('admin.dashboard'))
        
        if new_password != confirm_new_password:
            flash('New passwords do not match', 'error')
            return redirect(url_for('admin.dashboard'))
        
        # Verify current password
        if not check_password_hash(current_user.password_hash, current_password):
            flash('Current password is incorrect', 'error')
            return redirect(url_for('admin.dashboard'))
        
        # Update password
        current_user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
        flash('Password changed successfully', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error changing password: {str(e)}', 'error')
    
    return redirect(url_for('admin.dashboard'))


################################ DASHBOARD ###################################################################

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.role == 'admin' and not current_user.role == 'super_admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('auth.login'))
        
    office_data = []
    offices = Office.query.all()

    total_students = User.query.filter_by(role='student').count()
    total_office_admins = User.query.filter_by(role='office_admin').count()
    total_inquiries = Inquiry.query.count()
    pending_inquiries = Inquiry.query.filter_by(status='pending').count()
    resolved_inquiries = Inquiry.query.filter_by(status='resolved').count()

    # Example for determining top inquiries (by office with most inquiries)
    top_office = (
        db.session.query(Office.name, db.func.count(Inquiry.id).label('inquiry_count'))
        .join(Inquiry)
        .group_by(Office.id)
        .order_by(db.desc('inquiry_count'))
        .first()
    )
    top_inquiry_office = top_office.name if top_office else "N/A"

    for office in offices:
        inquiry_count = db.session.query(db.func.count(Inquiry.id)).filter(Inquiry.office_id == office.id).scalar()
        office_data.append({
            "name": office.name,
            "count": inquiry_count,
            "bg": "bg-blue-200"  # You can customize this per office if desired
        })

    return render_template(
        'admin/dashboard.html',
        offices=office_data,
        total_students=total_students,
        total_office_admins=total_office_admins,
        total_inquiries=total_inquiries,
        pending_inquiries=pending_inquiries,
        resolved_inquiries=resolved_inquiries,
        top_inquiry_office=top_inquiry_office
    )


############################################## ADMIN MANAGE #############################################

@admin_bp.route('/adminmanage')
def adminmanage():
    offices = Office.query.all()
    office_admins = User.query.filter_by(role='office_admin').all()
    
    # For quick stats
    total_offices = len(offices)
    active_office_admins = User.query.filter_by(role='office_admin', is_active=True).count()
    unassigned_offices = Office.query.filter(~Office.office_admins.any()).count()
    unassigned_admins = User.query.filter_by(role='office_admin').filter(~User.office_admin.has()).count()
    
    return render_template(
        'admin/adminmanage.html',
        offices=offices,
        office_admins=office_admins,
        total_offices=total_offices,
        active_office_admins=active_office_admins,
        unassigned_offices=unassigned_offices,
        unassigned_admins=unassigned_admins
    )

@admin_bp.route('/api/office/<int:office_id>/admins')
def get_office_admins(office_id):
    # Get the office
    office = Office.query.get_or_404(office_id)
    
    # Get all admins associated with this office
    office_admins = office.office_admins
    admins_data = []
    
    for office_admin in office_admins:
        user = office_admin.user
        if user:
            admins_data.append({
                'id': user.id,
                'first_name': user.first_name,
                'middle_name': user.middle_name,
                'last_name': user.last_name,
                'full_name': f"{user.first_name} {user.middle_name + ' ' if user.middle_name else ''}{user.last_name}",
                'email': user.email,
                'is_active': user.is_active,
                'created_at': user.created_at.strftime('%B %d, %I:%M %p')
            })
    
    return jsonify({'admins': admins_data})

@admin_bp.route('/remove_office_admin', methods=['POST'])
@login_required
def remove_office_admin():
    if not current_user.role == 'super_admin':
        return jsonify({'success': False, 'message': 'Unauthorized. Only super admins can remove office admins'}), 403
    
    try:
        data = request.json
        office_id = data.get('office_id')
        admin_id = data.get('admin_id')  
        
        if not office_id or not admin_id:
            return jsonify({'success': False, 'message': 'Missing required parameters'}), 400
        
        office = Office.query.get(office_id)
        if not office:
            return jsonify({'success': False, 'message': 'Office not found'}), 404
        
        admin = User.query.get(admin_id)
        if not admin or admin.role not in ['office_admin', 'super_admin']:
            return jsonify({'success': False, 'message': 'Admin not found'}), 404
        
        office_admin = OfficeAdmin.query.filter_by(office_id=office_id, user_id=admin_id).first()
        if not office_admin:
            return jsonify({'success': False, 'message': 'Admin not associated with this office'}), 404
        
        db.session.delete(office_admin)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Admin {admin.first_name} {admin.last_name} has been removed from {office.name}'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/add_admin', methods=['POST'])
def add_admin():
    try:
        # Get form data
        first_name = request.form.get('first_name')
        middle_name = request.form.get('middle_name', '')  # Optional
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        office_id = request.form.get('office_id')
        is_active = request.form.get('is_active') == 'true'
        
        if not all([first_name, last_name, email, password]):
            return jsonify({'success': False, 'message': 'Please fill all required fields'}), 400
        
        if password != confirm_password:
            return jsonify({'success': False, 'message': 'Passwords do not match'}), 400
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'success': False, 'message': 'Email already exists'}), 400
        
        profile_pic_path = None
        if 'profile_pic' in request.files:
            profile_pic = request.files['profile_pic']
            if profile_pic and profile_pic.filename != '':
                # Save profile picture
                filename = secure_filename(profile_pic.filename)
                # Create upload folder if it doesn't exist
                upload_folder = os.path.join(current_app.root_path, 'static/uploads/profiles')
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                
                # Save file
                profile_pic_path = os.path.join('uploads/profiles', filename)
                profile_pic.save(os.path.join(current_app.root_path, 'static', profile_pic_path))
        
        new_user = User(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            email=email,
            password_hash=generate_password_hash(password),
            role='office_admin',
            is_active=is_active,
            profile_pic=profile_pic_path
        )
        
        db.session.add(new_user)
        db.session.flush()
        
        if office_id and office_id != '':
            office = Office.query.get(office_id)
            if office:
                office_admin = OfficeAdmin(
                    user_id=new_user.id,
                    office_id=int(office_id)
                )
                db.session.add(office_admin)
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Office admin added successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error adding office admin: {str(e)}'}), 500


@admin_bp.route('/api/admin/<int:admin_id>', methods=['GET'])
def get_admin_data(admin_id):
    try:
        admin = User.query.filter_by(id=admin_id, role='office_admin').first()
        
        if not admin:
            return jsonify({'success': False, 'message': 'Admin not found'}), 404
        
        # Get office assignment
        office_admin = OfficeAdmin.query.filter_by(user_id=admin_id).first()
        office_id = office_admin.office_id if office_admin else None
        
        return jsonify({
            'success': True,
            'admin': {
                'id': admin.id,
                'first_name': admin.first_name,
                'middle_name': admin.middle_name,
                'last_name': admin.last_name,
                'email': admin.email,
                'is_active': admin.is_active,
                'office_id': office_id
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error fetching admin data: {str(e)}'}), 500

@admin_bp.route('/delete_admin', methods=['POST'])
def delete_admin():
    try:
        admin_id = request.form.get('admin_id')
        
        if not admin_id:
            flash('Admin ID is required', 'error')
            return redirect(url_for('admin.adminmanage'))
        
        admin = User.query.filter_by(id=admin_id, role='office_admin').first()
        
        if not admin:
            flash('Admin not found', 'error')
            return redirect(url_for('admin.adminmanage'))
        
        # Delete the admin
        db.session.delete(admin)
        db.session.commit()
        
        flash('Admin deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting admin: {str(e)}', 'error')
    
    return redirect(url_for('admin.adminmanage'))

@admin_bp.route('/manage-admins')
def manage_admins():
    offices = Office.query.all()
    office_admins = User.query.filter_by(role='office_admin').all()
    
    # For quick stats
    total_offices = len(offices)
    active_office_admins = User.query.filter_by(role='office_admin', is_active=True).count()
    unassigned_offices = Office.query.filter(~Office.office_admins.any()).count()
    unassigned_admins = User.query.filter_by(role='office_admin').filter(~User.office_admin.has()).count()
    
    return render_template(
        'admin/adminmanage.html',
        offices=offices,
        office_admins=office_admins,
        total_offices=total_offices,
        active_office_admins=active_office_admins,
        unassigned_offices=unassigned_offices,
        unassigned_admins=unassigned_admins
    )

@admin_bp.route('/update_admin', methods=['POST'])
def update_admin():
    try:
        # Get form data
        admin_id = request.form.get('admin_id')
        first_name = request.form.get('first_name')
        middle_name = request.form.get('middle_name', '')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        office_id = request.form.get('office_id')
        is_active = request.form.get('is_active') == 'true'
        
        if not all([admin_id, first_name, last_name, email]):
            return jsonify({'success': False, 'message': 'Please fill all required fields'}), 400
        
        admin = User.query.filter_by(id=admin_id, role='office_admin').first()
        if not admin:
            return jsonify({'success': False, 'message': 'Admin not found'}), 404
        
        existing_user = User.query.filter(User.email == email, User.id != admin_id).first()
        if existing_user:
            return jsonify({'success': False, 'message': 'Email already exists for another user'}), 400
        
        # Update admin user information
        admin.first_name = first_name
        admin.middle_name = middle_name
        admin.last_name = last_name
        admin.email = email
        admin.is_active = is_active
        
        # Update office assignment if provided
        if office_id:
            # Check if admin already has an office assignment
            existing_office_admin = OfficeAdmin.query.filter_by(user_id=admin_id).first()
            
            if existing_office_admin:
                # Update existing assignment
                existing_office_admin.office_id = int(office_id)
            else:
                # Create new assignment
                new_office_admin = OfficeAdmin(
                    user_id=admin_id,
                    office_id=int(office_id)
                )
                db.session.add(new_office_admin)
        
        # Commit changes to database
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Admin updated successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error updating admin: {str(e)}'}), 500

@admin_bp.route('/api/offices', methods=['GET'])
def get_offices():
    try:
        offices = Office.query.all()
        
        return jsonify({
            'success': True,
            'offices': [{'id': office.id, 'name': office.name} for office in offices]
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error fetching offices: {str(e)}'}), 500

#####################################################################################################################

@admin_bp.route('/inquiry-logs')
def inquiry_logs():
    return "Inquiry Logs page under construction"

@admin_bp.route('/announcement')
def announcement():
    return "Announcement page under construction"