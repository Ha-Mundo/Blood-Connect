""" Main Blueprint for core views and global handlers """

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required, logout_user

from app.forms import ProfileForm
from app.services.main_service import MainService

main_bp = Blueprint('main', __name__)


# --- GLOBAL HANDLERS ---
@main_bp.before_app_request
def check_banned_user():
    if current_user.is_authenticated and not current_user.is_active:
        logout_user()
        flash("Your account has been suspended by an administrator.", "danger")
        return redirect(url_for('auth.login'))


@main_bp.app_context_processor
def inject_global_data():
    stats = MainService.get_global_stats(current_user)
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
        admin_stats = MainService.get_admin_stats()

    return render_template('index.html', admin_stats=admin_stats)


@main_bp.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    is_admin = current_user.role == "admin"
    

    if form.validate_on_submit():
        MainService.update_profile(current_user, form)
        flash("Profile updated successfully!", "success")
        return redirect(url_for('main.profile'))

    if request.method == 'GET':
        form.username.data = current_user.username
        form.blood_group.data = (
            current_user.blood_group.upper()
            if current_user.blood_group else ''
        )
        form.email_notifications.data = current_user.email_notifications

    activity = {'completed_donations': 0, 'completed_requests': 0}

    if current_user.role != 'admin':
        activity = MainService.get_user_activity(current_user)

    return render_template(
        'profile.html',
        form=form,
        is_admin=is_admin,
        completed_donations=activity['completed_donations'],
        completed_requests=activity['completed_requests']
    )