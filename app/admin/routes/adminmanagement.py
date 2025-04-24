from app.models import Inquiry, InquiryMessage, User, Office, db, OfficeAdmin, Student, CounselingSession, StudentActivityLog, SuperAdminActivityLog, OfficeLoginLog, AuditLog
from flask import Blueprint, redirect, url_for, render_template, jsonify, request, flash, Response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, current_user
from flask_socketio import emit
from app import socketio
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from sqlalchemy import func, case, or_
import random
import os
from app.admin import admin_bp



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
        first_name = request.form.get('first_name', '').strip()
        middle_name = request.form.get('middle_name', '')  # Optional
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        office_id = request.form.get('office_id')
        
        # Set is_active to False by default for new admins
        is_active = False
        
        # Validate required fields aren't empty
        if not first_name:
            return jsonify({'success': False, 'message': 'First name is required'}), 400
        if not last_name:
            return jsonify({'success': False, 'message': 'Last name is required'}), 400
        if not email:
            return jsonify({'success': False, 'message': 'Email is required'}), 400
        if not password:
            return jsonify({'success': False, 'message': 'Password is required'}), 400
        
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
        
        # Update profile picture if provided
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
                
                # Update the admin's profile pic path
                admin.profile_pic = profile_pic_path
        
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
    
@admin_bp.route('/reset_admin_password', methods=['POST'])
def reset_admin_password():
    try:
        admin_id = request.form.get('admin_id')
        
        if not admin_id:
            return jsonify({'success': False, 'message': 'Admin ID is required'}), 400
        
        admin = User.query.filter_by(id=admin_id, role='office_admin').first()
        if not admin:
            return jsonify({'success': False, 'message': 'Admin not found'}), 404
        
        # Generate a 4-digit default password
        import random
        default_password = ''.join(random.choices('0123456789', k=4))
        
        # Update password
        admin.password_hash = generate_password_hash(default_password)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Password reset successfully', 
            'password': default_password
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error resetting password: {str(e)}'}), 500

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