""" Main Blueprint for core views and global handlers """
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required, logout_user

from app.extensions import db, bcrypt
from app.models import User, BloodDonation, BloodRequest
from app.forms import ProfileForm

main_bp = Blueprint('main', __name__)

# --- GLOBAL HANDLERS ---
@main_bp.before_app_request
def check_banned_user():
    """ Log out banned users globally """
    if current_user.is_authenticated and not current_user.is_active:
        logout_user()
        flash("Your account has been suspended by an administrator.", "danger")
        return redirect(url_for('auth.login'))

@main_bp.app_context_processor
def inject_global_data():
    """ Inject global stats into all templates """
    stats = {'donations': 0, 'requests': 0, 'total_available': 0}
    stats['total_available'] = BloodDonation.query.filter_by(status='Approved').count()
    
    if current_user.is_authenticated:
        stats['donations'] = BloodDonation.query.filter_by(email=current_user.email, status='Completed').count()
        stats['requests'] = BloodRequest.query.filter_by(requester_email=current_user.email, status='Completed').count()
        
    return dict(user_stats=stats)

# --- ERROR HANDLERS ---
@main_bp.app_errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404, error_message="Page not found."), 404

@main_bp.app_errorhandler(403)
def forbidden(e):
    return render_template('error.html', error_code=403, error_message="Permission denied."), 403

@main_bp.app_errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error_code=500, error_message="Unexpected server error."), 500

@main_bp.app_errorhandler(405)
def method_not_allowed(e):
    return render_template('error.html', error_code=405, error_message="Method not allowed."), 405

@main_bp.app_errorhandler(429)
def ratelimit_handler(e):
    flash(f"Too many requests. {e.description}", "danger")
    return redirect(url_for('auth.login'))

# --- ROUTES ---
@main_bp.route("/")
def home():
    admin_stats = {}
    if current_user.is_authenticated and current_user.role == 'admin':
        admin_stats['total_users'] = User.query.count()
        admin_stats['total_donations'] = BloodDonation.query.count()
        admin_stats['total_requests'] = BloodRequest.query.count()
        
    return render_template('index.html', admin_stats=admin_stats)

@main_bp.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    
    if form.validate_on_submit():
        if form.username.data:
            current_user.username = form.username.data.lower()
        if form.blood_group.data:
            current_user.blood_group = form.blood_group.data.lower()
        if form.new_password.data:
            hashed_pw = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            current_user.password = hashed_pw
            
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('main.profile'))
        
    elif request.method == 'GET':
        form.username.data = current_user.username.title()
        form.blood_group.data = current_user.blood_group.upper() if current_user.blood_group else ''

    completed_donations, completed_requests = 0, 0
    if current_user.role != 'admin':
        completed_donations = BloodDonation.query.filter_by(email=current_user.email, status='Completed').count()
        completed_requests = BloodRequest.query.filter_by(requester_email=current_user.email, status='Completed').count()

    return render_template('profile.html', form=form, completed_donations=completed_donations, completed_requests=completed_requests)