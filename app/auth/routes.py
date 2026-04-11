""" Authentication Blueprint """

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user, login_required

from app.extensions import limiter
from app.forms import (
    RegistrationForm,
    LoginForm,
    ForgotPasswordForm,
    ResetPasswordForm
)
from app.security import is_safe_url
from app.services import AuthService, EmailService


auth_bp = Blueprint('auth', __name__)


# -------------------
# LOGIN
# -------------------
@auth_bp.route("/login", methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = LoginForm()

    if form.validate_on_submit():
        user, error = AuthService.authenticate(
            form.email.data,
            form.password.data
        )

        if error:
            flash(error, "danger")
            return render_template('login.html', form=form)

        login_user(
            user,
            remember=getattr(form, "remember", None) and form.remember.data
        )

        flash(f"Welcome back, {user.username}!", "success")

        next_page = request.args.get('next')
        if next_page and is_safe_url(next_page, request.host_url):
            return redirect(next_page)

        return redirect(url_for('main.home'))

    return render_template('login.html', form=form)


# -------------------
# REGISTER
# -------------------
@auth_bp.route("/register", methods=['GET', 'POST'])
@limiter.limit("3 per minute")
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = RegistrationForm()

    if form.validate_on_submit():
        user, error = AuthService.register(
            form.username.data,
            form.email.data,
            form.password.data
        )

        if error:
            flash(error, "danger")
            return render_template('register.html', form=form)

        token = AuthService.generate_email_token(user.email)
        EmailService.send_confirmation_email(user, token)

        flash("A confirmation email has been sent. Check your inbox.", "info")
        return redirect(url_for('auth.login'))

    return render_template('register.html', form=form)


# -------------------
# EMAIL CONFIRMATION
# -------------------
@auth_bp.route('/confirm/<token>')
def confirm_email(token):
    email, error = AuthService.verify_token(
        token,
        'email-confirm',
        3600
    )

    if error:
        flash(error, "danger")
        return redirect(url_for('auth.login'))

    user, error = AuthService.confirm_user(email)

    if error:
        flash(error, "danger")
        return redirect(url_for('auth.login'))

    flash("Account confirmed successfully! You can now log in.", "success")
    return render_template('verified_success.html')


# -------------------
# LOGOUT
# -------------------
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('main.home'))


# -------------------
# RESET REQUEST
# -------------------
@auth_bp.route("/reset_password_request", methods=['GET', 'POST'])
@limiter.limit("3 per minute")
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
        
    form = ForgotPasswordForm()

    if form.validate_on_submit():
        user = AuthService.get_user_by_email(form.email.data)

        if user and user.is_active:
            token = AuthService.generate_reset_token(user.email)
            EmailService.send_reset_email(user, token)

        # neutral answer (anti-enumeration)
        flash("If the email exists, you will receive reset instructions.", "info")
        return redirect(url_for('auth.login'))
        
    return render_template('reset_request.html', form=form)


# -------------------
# RESET PASSWORD
# -------------------
@auth_bp.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
        
    email, error = AuthService.verify_token(
        token,
        'password-reset',
        1800
    )

    if error:
        flash(error, "danger")
        return redirect(url_for('auth.reset_password_request'))

    form = ResetPasswordForm()

    if form.validate_on_submit():
        error = AuthService.reset_password(email, form.password.data)

        if error:
            flash(error, "danger")
            return redirect(url_for('auth.login'))

        flash("Your password has been updated! You can now log in.", "success")
        return redirect(url_for('auth.login'))
        
    return render_template('reset_token.html', form=form)