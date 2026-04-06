""" Authentication Blueprint """
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from flask import current_app

from app.extensions import db, bcrypt, mail, limiter
from app.models import User
from app.forms import RegistrationForm, LoginForm, ForgotPasswordForm, ResetPasswordForm
from app.utils import generate_confirmation_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login", methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            if not user.is_active:
                flash("Your account has been suspended for violating our terms.", "danger")
                return redirect(url_for('auth.login'))
            
            if not user.is_verified:
                flash("You need to verify your email first! Check your inbox.", "warning")
                return redirect(url_for('auth.login'))
            
            login_user(user, remember=True)
            flash(f"Welcome back, {user.username}!", "success")
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash("Login Unsuccessful. Please check email and password.", "danger")
            
    return render_template('login.html', form=form)

@auth_bp.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter(
            (User.username == form.username.data) | 
            (User.email == form.email.data.lower())
        ).first()

        if existing_user:
            flash("Username or Email already registered.", "danger")
            return render_template('register.html', form=form)

        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data.lower(), password=hashed_pw)
        db.session.add(user)
        db.session.commit()

        token = generate_confirmation_token(user.email)
        confirm_url = url_for('auth.confirm_email', token=token, _external=True)
        html_body = f"<p>Welcome! Click here to confirm your account: <a href='{confirm_url}'>Confirm Email</a></p>"
        msg = Message("Confirm your account", recipients=[user.email])
        msg.html = html_body
        mail.send(msg)

        flash("A confirmation email has been sent. Check it out to log in.", "info")
        return redirect(url_for('auth.login'))
        
    return render_template('register.html', form=form)

@auth_bp.route('/confirm/<token>')
def confirm_email(token):
    try:
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        email = serializer.loads(token, salt='email-confirm-salt', max_age=3600)
    except:
        flash("The confirmation link is invalid or expired.", "danger")
        return redirect(url_for('auth.login'))
        
    user = User.query.filter_by(email=email).first_or_404()
    if user.is_verified:
        flash("Account already confirmed. Please log in.", "success")
    else:
        user.is_verified = True
        db.session.commit()
        flash("Account confirmed successfully! You can now log in.", "success")
        
    return render_template('verified_success.html')

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('main.home'))

@auth_bp.route("/reset_password_request", methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
        
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            token = generate_confirmation_token(user.email)
            reset_url = url_for('auth.reset_token', token=token, _external=True)
            msg = Message("Password Reset Request", recipients=[user.email])
            msg.body = f"To reset your password, visit: {reset_url}\nIf you didn't request this, ignore."
            mail.send(msg)
            
        flash("An email has been sent with instructions to reset your password.", "info")
        return redirect(url_for('auth.login'))
        
    return render_template('reset_request.html', form=form)

@auth_bp.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
        
    try:
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        email = serializer.loads(token, salt='email-confirm-salt', max_age=1800)
    except:
        flash("The reset link is invalid or has expired.", "danger")
        return redirect(url_for('auth.reset_password_request'))
        
    user = User.query.filter_by(email=email).first_or_404()
    form = ResetPasswordForm()
    
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_pw
        db.session.commit()
        flash("Your password has been updated! You can now log in.", "success")
        return redirect(url_for('auth.login'))
        
    return render_template('reset_token.html', form=form)