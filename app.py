import os
import datetime
from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

# Local imports
from forms import DonationForm, RequestForm, RegistrationForm, LoginForm, ForgotPasswordForm, ResetPasswordForm
from time_limit import threshold_donation, threshold_request, is_action_allowed

# 1. INITIALIZATION & CONFIG
load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-very-unsafe')

# Secure Database Path (Instance folder)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'instance', 'BloodDonationSystem.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Mail configuration for Mailpit (local testing)
app.config['MAIL_SERVER'] = 'localhost'      # Mailpit runs locally
app.config['MAIL_PORT'] = 1025               # default Mailpit SMTP port
app.config['MAIL_USE_TLS'] = False           # no TLS needed for local testing
app.config['MAIL_USE_SSL'] = False           # no SSL needed
app.config['MAIL_DEFAULT_SENDER'] = ('Blood Donation System', 'test@mail.com')  # default sender email
# No username/password needed for Mailpit
# app.config['MAIL_USERNAME'] = None
# app.config['MAIL_PASSWORD'] = None
mail = Mail(app)

# Token generator
def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='email-confirm-salt')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Initialize Flask-Limiter (using memory storage for simplicity)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["500 per day", "100 per hour"],
    storage_uri="memory://"
)

# 2. MODELS
class User(db.Model, UserMixin):
    """ User model for both Admins and regular Donors/Receivers """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False) 
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(10), default='user')
    is_verified = db.Column(db.Boolean, nullable=False, default=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True) # True = Active, False = Banned

class BloodDonation(db.Model):
    """ Model to store blood donation records """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    blood_groups = db.Column(db.String(5), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    latest_donation = db.Column(db.Date, nullable=False)
    next_donation = db.Column(db.Date)
    donation_counter = db.Column(db.Integer, default=1)
    status = db.Column(db.String(20), nullable=False, default='Pending')

class BloodRequest(db.Model):
    """ Model to track blood requests made by users """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    blood_groups = db.Column(db.String(5), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    requester_email = db.Column(db.String(120), nullable=False)  
    donor_email = db.Column(db.String(120), nullable=False)     
    request_date = db.Column(db.Date, nullable=False, default=datetime.date.today)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    
# Handle the 429 error gracefully so the user sees a Bootstrap flash message
@app.errorhandler(429)
def ratelimit_handler(e):
    """ Handle rate limit exceeded errors """
    flash(f"Too many requests. {e.description}", "danger")
    return redirect(url_for('login'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- NEW CHECK - AUTO-LOGOUT ---
@app.before_request
def check_banned_user():
    """ Instantly log out users who have been banned while actively browsing """
    if current_user.is_authenticated and not current_user.is_active:
        logout_user()
        flash("Your account has been suspended by an administrator.", "danger")
        return redirect(url_for('login'))

# --- CONTEXT PROCESSOR FOR STATS ---
@app.context_processor
def inject_global_data():
    """ Inject global stats into all templates (base.html, index.html, etc.) """
    stats = {'donations': 0, 'requests': 0, 'total_available': 0}
    
    # Count ONLY the blood that is physically available to be requested
    stats['total_available'] = BloodDonation.query.filter_by(status='Pending').count()
    
    if current_user.is_authenticated:
        # Count ONLY donations and requests that have been successfully completed
        stats['donations'] = BloodDonation.query.filter_by(email=current_user.email, status='Completed').count()
        stats['requests'] = BloodRequest.query.filter_by(requester_email=current_user.email, status='Completed').count()
        
    return dict(user_stats=stats)

# 3. ROUTES
@app.route("/")
def home():
    """ Main dashboard """
    admin_stats = {}
    if current_user.is_authenticated and current_user.role == 'admin':
        admin_stats['total_users'] = User.query.count()
        admin_stats['total_donations'] = BloodDonation.query.count()
        admin_stats['total_requests'] = BloodRequest.query.count()
        
    return render_template('index.html', admin_stats=admin_stats)

@app.route("/login", methods=['GET', 'POST'])
@limiter.limit("5 per minute")  # Limit login attempts to 5 per minute per IP
def login():
    """ Handle user login with secure password verification """
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            if not user.is_active:
                flash("Your account has been suspended for violating our terms.", "danger")
                return redirect(url_for('login'))
            
            if not user.is_verified:
                flash("You need to verify your email first! Check your inbox.", "warning")
                return redirect(url_for('login'))
            
            login_user(user, remember=True)
            flash(f"Welcome back, {user.username}!", "success")
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash("Login Unsuccessful. Please check email and password.", "danger")
            
    return render_template('login.html', form=form)

@app.route("/register", methods=['GET', 'POST'])
def register():
    """ Handle new user registration with duplicate check """
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter(
            (User.username == form.username.data) | 
            (User.email == form.email.data.lower())
        ).first()

        if existing_user:
            flash("Username or Email already registered. Please use different credentials.", "danger")
            return render_template('register.html', form=form)

        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data.lower(), password=hashed_pw)
        db.session.add(user)
        db.session.commit()

        # Generate token and send email
        token = generate_confirmation_token(user.email)
        confirm_url = url_for('confirm_email', token=token, _external=True)
        html_body = f"<p>Welcome! Click here to confirm your account: <a href='{confirm_url}'>Confirm Email</a></p>"
        msg = Message("Confirm your account", sender=("Blood Donation System", "test@mail.com"), recipients=[user.email])
        msg.html = html_body
        mail.send(msg)

        flash("A confirmation email has been sent to your address. Check it out to log in.", "info")
        return redirect(url_for('login'))
        
    return render_template('register.html', form=form)

# 2. New route for token verification
@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        email = serializer.loads(token, salt='email-confirm-salt', max_age=3600) # 1 hour expiration
    except:
        flash("The confirmation link is invalid or expired.", "danger")
        return redirect(url_for('login'))
        
    user = User.query.filter_by(email=email).first_or_404()
    if user.is_verified:
        flash("Account already confirmed. Please log in.", "success")
    else:
        user.is_verified = True
        db.session.commit()
        flash("Account confirmed successfully! You can now log in.", "success")
        
    return redirect(url_for('login'))

@app.route("/logout")
@login_required
def logout():
    """ Handle user logout """
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))

# --- PASSWORD RESET ROUTES ---
@app.route("/reset_password_request", methods=['GET', 'POST'])
def reset_password_request():
    """ Route to request a password reset link """
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            # Generate token and send email
            token = generate_confirmation_token(user.email)
            reset_url = url_for('reset_token', token=token, _external=True)
            msg = Message("Password Reset Request", 
                          sender=app.config['MAIL_DEFAULT_SENDER'], 
                          recipients=[user.email])
            msg.body = f"To reset your password, visit the following link: {reset_url}\nIf you did not make this request, ignore this email."
            mail.send(msg)
            
        # Flash the same message regardless of email existence for security (don't reveal users)
        flash("An email has been sent with instructions to reset your password.", "info")
        return redirect(url_for('login'))
        
    return render_template('reset_request.html', form=form)

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    """ Route to update password via valid token """
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        
    try:
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        # Token expires after 30 minutes (1800 seconds)
        email = serializer.loads(token, salt='email-confirm-salt', max_age=1800)
    except:
        flash("The reset link is invalid or has expired.", "danger")
        return redirect(url_for('reset_password_request'))
        
    user = User.query.filter_by(email=email).first_or_404()
    form = ResetPasswordForm()
    
    if form.validate_on_submit():
        # Hash the new password and update user record
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_pw
        db.session.commit()
        flash("Your password has been updated! You can now log in.", "success")
        return redirect(url_for('login'))
        
    return render_template('reset_token.html', form=form)

@app.route("/blood_donation", methods=['GET', 'POST'])
@login_required
def blood_donation():
    """ Register a new donation or view current donation status """
    today = datetime.date.today()
    latest_donation = BloodDonation.query.filter_by(email=current_user.email).order_by(BloodDonation.id.desc()).first()
    
    # Check if user explicitly clicked 'Make a new donation attempt'
    force_form = request.args.get('new') == '1'
    active_donation = None
    
    if latest_donation and not force_form:
        # Show status for ongoing, cancelled, or unsuccessful donations
        if latest_donation.status in ['Pending', 'Claimed', 'Cancelled', 'Unsuccessful']:
            active_donation = latest_donation
        # Enforce cooldown ONLY if the previous one was successfully completed
        elif latest_donation.status == 'Approved' and not is_action_allowed(latest_donation.next_donation, today):
            active_donation = latest_donation

    form = DonationForm()
    if request.method == 'GET':
        form.name.data = current_user.username
        form.email.data = current_user.email
    
    if form.validate_on_submit() and not active_donation:
        email = form.email.data.lower()
        
        # Double-check cooldown for Approved donations at the logic level
        if latest_donation and latest_donation.status == 'Approved' and not is_action_allowed(latest_donation.next_donation, today):
            flash("Safety limit: You can only donate once every 90 days after a successful donation.", "danger")
            return redirect(url_for('blood_donation'))

        new_donor = BloodDonation(
            name=form.name.data.lower(), 
            age=form.age.data,
            blood_groups=form.blood_groups.data.lower(), 
            city=form.city.data.lower(),
            email=email, 
            latest_donation=today, 
            next_donation=threshold_donation(today),
            donation_counter=(latest_donation.donation_counter + 1 if latest_donation else 1),
            status='Pending'
        )
        db.session.add(new_donor)
        db.session.commit()
        flash("Registration successful!", "success")
        return redirect(url_for('blood_donation'))
        
    return render_template('donate.html', form=form, active_donation=active_donation)

@app.route("/cancel_donation/<int:id>", methods=['POST'])
@login_required
def cancel_donation(id):
    """ Allow users to cancel their own pending donations """
    donation = BloodDonation.query.get_or_404(id)
    
    # Security check: ensure the user owns this donation and it's pending
    if donation.email == current_user.email and donation.status == 'Pending':
        db.session.delete(donation) # we remove the record from the database
        db.session.commit()
        flash("Your donation has been cancelled.", "info")
    else:
        flash("Action not allowed.", "danger")
        
    return redirect(url_for('blood_donation'))

@app.route("/blood_receive", methods=['GET', 'POST'])
@login_required
def blood_receive():
    """ Search for donors or view current pending request """
    
    # 1. Fetch the user's most recent request
    latest_request = BloodRequest.query.filter_by(requester_email=current_user.email).order_by(BloodRequest.id.desc()).first()
    
    force_form = request.args.get('new') == '1'
    active_request = None
    
    if latest_request and not force_form:
        # Show status view for ongoing or failed requests. 
        # If 'Fulfilled' / 'Cancelled', active_request remains None so the form resets automatically.
        if latest_request.status in ['Pending', 'Approved', 'Unsuccessful']:
            active_request = latest_request
            
    form = RequestForm()
    
    # If there's an active request blocking the UI, render the status view immediately
    if active_request:
        return render_template('find_blood.html', form=form, active_request=active_request)

    # 2. Search logic (only runs if NO active requests)
    city = request.form.get('city') or request.args.get('city')
    bg = request.form.get('blood_groups') or request.args.get('bg')
    
    if city and bg:
        page = request.args.get('page', 1, type=int)
        
        # CRITICAL FIX: Only search for donations that are 'Pending' (available)
        pagination = BloodDonation.query.filter_by(
            blood_groups=bg.lower(),
            city=city.lower(),
            status='Pending' 
        ).paginate(page=page, per_page=10, error_out=False)
        
        if not pagination.items:
            return render_template('empty_db.html')
            
        return render_template('results.html', pagination=pagination, city=city, bg=bg)
                               
    return render_template('find_blood.html', form=form, active_request=None)

@app.route("/cancel_request/<int:id>", methods=['POST'])
@login_required
def cancel_request(id):
    """ Soft cancel the request and free up the claimed donation """
    blood_req = BloodRequest.query.get_or_404(id)
    
    if blood_req.requester_email == current_user.email and blood_req.status == 'Pending':
        
        # 1. Find the claimed donation and make it available again
        donation = BloodDonation.query.filter_by(
            email=blood_req.donor_email, 
            blood_groups=blood_req.blood_groups,
            status='Claimed'
        ).first()
        
        if donation:
            donation.status = 'Pending'
            
        # 2. Soft Delete we update the status to cancelled
        blood_req.status = 'Cancelled'
        db.session.commit()
        
        flash("Blood request cancelled. The donation is now available for others.", "info")
    else:
        flash("Action not allowed.", "danger")
        
    return redirect(url_for('blood_receive'))

@app.route("/take_donation", methods=['POST'])
@login_required
def take_donation():
    """ Process a blood request and change donation status instead of deleting """
    donation_id = request.form.get('id')
    donation = BloodDonation.query.get_or_404(donation_id)
    today = datetime.date.today()

    if donation.email == current_user.email:
        flash("You cannot request your own donation!", "warning")
        return redirect(url_for('home'))

    # Apply limit ONLY if last request is active or successful
    last_request = BloodRequest.query.filter_by(requester_email=current_user.email).order_by(BloodRequest.id.desc()).first()
    if last_request and last_request.status in ['Pending', 'Approved', 'Fulfilled']:
        allowed_date = threshold_request(last_request.request_date)
        if not is_action_allowed(allowed_date, today):
            flash("Safety limit: You can only make one request every 7 days.", "danger")
            return redirect(url_for('home'))
    
    new_request = BloodRequest(
        name=current_user.username.lower(),
        blood_groups=donation.blood_groups,
        city=donation.city,
        requester_email=current_user.email,  
        donor_email=donation.email,          
        request_date=today,
        status='Pending'
    )
    
    db.session.add(new_request)
    donation.status = 'Claimed'
    db.session.commit()
    
    flash("Request successful! Notification sent.", "success")
    return redirect(url_for('blood_receive'))

@app.route("/all_donations_db")
@login_required
@limiter.exempt
def all_donations_db():
    """ Admin only: View and filter all donation records paginated """
    if current_user.role != 'admin':
        abort(403) 
        
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search')
    blood_group = request.args.get('blood_group')
    status = request.args.get('status')

    # Base query
    query = BloodDonation.query

    # Apply Search (Name, Email, or City) - Forcing lowercase to match DB entries
    if search:
        search_term = search.lower()
        query = query.filter(
            (BloodDonation.name.contains(search_term)) | 
            (BloodDonation.email.contains(search_term)) |
            (BloodDonation.city.contains(search_term))
        )

    # Apply Blood Group Filter
    if blood_group:
        query = query.filter_by(blood_groups=blood_group.lower())

    # Apply Status Filter
    if status:
        query = query.filter_by(status=status)

    # Paginate and count filtered records
    pagination = query.order_by(BloodDonation.id.desc()).paginate(page=page, per_page=10, error_out=False)
    count = query.count()
    
    return render_template('donation_db.html', pagination=pagination, all_donations_counter=count)

@app.route("/update_donation_status/<int:id>", methods=['POST'])
@login_required
@limiter.exempt
def update_donation_status(id):
    """ Admin only: Update the status of a blood donation and notify user """
    if current_user.role != 'admin':
        abort(403)
        
    donation = BloodDonation.query.get_or_404(id)
    new_status = request.form.get('new_status')
    
    # Validation for allowed statuses
    allowed_statuses = ['Pending', 'Claimed', 'Approved', 'Completed', 'Unsuccessful', 'Cancelled']
    
    if new_status in allowed_statuses:
        donation.status = new_status
        db.session.commit()
        
        # Send email notification if Approved
        if new_status == 'Approved':
            try:
                msg = Message("Blood Donation Approved", 
                              sender=app.config['MAIL_DEFAULT_SENDER'], 
                              recipients=[donation.email])
                msg.body = f"Hello {donation.name.capitalize()},\n\nGreat news! Your blood donation has been Approved. Thank you for your contribution to the community."
                mail.send(msg)
            except Exception as e:
                # Failsafe so the app doesn't crash if the mail server is down
                flash("Status updated, but email notification failed to send.", "warning")

        flash(f"Donation #{id} updated to {new_status}.", "success")
    else:
        flash("Invalid status update.", "danger")
        
    return redirect(url_for('all_donations_db'))

@app.route("/all_requests_db")
@login_required
@limiter.exempt
def all_requests_db():
    """ Admin only: View and filter all blood requests paginated """
    if current_user.role != 'admin':
        abort(403)
        
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search')
    blood_group = request.args.get('blood_group')
    status = request.args.get('status')

    # Base query
    query = BloodRequest.query

    # Apply Search (Name, Requester Email, or City)
    if search:
        search_term = search.lower()
        query = query.filter(
            (BloodRequest.name.contains(search_term)) | 
            (BloodRequest.requester_email.contains(search_term)) |
            (BloodRequest.city.contains(search_term))
        )

    # Apply Blood Group Filter
    if blood_group:
        query = query.filter_by(blood_groups=blood_group.lower())

    # Apply Status Filter
    if status:
        query = query.filter_by(status=status)

    # Paginate and count filtered records
    pagination = query.order_by(BloodRequest.id.desc()).paginate(page=page, per_page=10, error_out=False)
    count = query.count()
    
    return render_template('request_db.html', pagination=pagination, all_requests_counter=count)

@app.route("/update_request_status/<int:id>", methods=['POST'])
@login_required
@limiter.exempt
def update_request_status(id):
    """ Admin only: Update blood request status, handle rollbacks, and notify user """
    if current_user.role != 'admin':
        abort(403)
        
    blood_req = BloodRequest.query.get_or_404(id)
    new_status = request.form.get('new_status')
    
    allowed_statuses = ['Pending', 'Approved', 'Completed', 'Unsuccessful', 'Cancelled']
    
    if new_status in allowed_statuses:
        # ROLLBACK LOGIC: If the request fails, free the reserved blood
        if new_status in ['Cancelled', 'Unsuccessful']:
            donation = BloodDonation.query.filter_by(
                email=blood_req.donor_email, 
                blood_groups=blood_req.blood_groups,
                status='Claimed'
            ).first()
            
            if donation:
                donation.status = 'Pending'

        blood_req.status = new_status
        db.session.commit()

        # --- SENDING EMAIL NOTIFICATIONS ---
        try:
            if new_status == 'Approved':
                msg = Message("Blood Request Approved", 
                              sender=app.config['MAIL_DEFAULT_SENDER'], 
                              recipients=[blood_req.requester_email])
                msg.body = f"Hello {blood_req.name.capitalize()},\n\nYour blood request for group {blood_req.blood_groups.upper()} in {blood_req.city.capitalize()} has been Approved. We are coordinating the next steps."
                mail.send(msg)

            elif new_status == 'Unsuccessful':
                msg = Message("Blood Request Update", 
                              sender=app.config['MAIL_DEFAULT_SENDER'], 
                              recipients=[blood_req.requester_email])
                msg.body = f"Hello {blood_req.name.capitalize()},\n\nWe regret to inform you that your blood request for group {blood_req.blood_groups.upper()} could not be fulfilled at this time and has been marked as {new_status}."
                mail.send(msg)
                
        except Exception as e:
            flash("Status updated, but email notification failed.", "warning")

        flash(f"Blood Request #{id} updated to {new_status}.", "success")
    else:
        flash("Invalid status update.", "danger")
        
    return redirect(url_for('all_requests_db'))

@app.route("/all_users_db")
@login_required
@limiter.exempt
def all_users_db():
    if current_user.role != 'admin':
        abort(403)
    
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search')
    status = request.args.get('status')
    verified = request.args.get('verified')

    # Base query
    query = User.query

    # Apply Search (Username or Email)
    if search:
        query = query.filter((User.username.contains(search)) | (User.email.contains(search)))

    # Apply Status Filter (Active/Banned)
    if status:
        is_active = True if status == 'active' else False
        query = query.filter_by(is_active=is_active)

    # Apply Verification Filter
    if verified in ['1', '0']:
        is_verified = True if verified == '1' else False
        query = query.filter_by(is_verified=is_verified)

    pagination = query.order_by(User.id.desc()).paginate(page=page, per_page=10, error_out=False)
    count = query.count()
    
    return render_template('users_db.html', pagination=pagination, all_users_counter=count)

@app.route("/update_users_status/<int:user_id>", methods=['POST'])
@login_required
@limiter.exempt
def toggle_user(user_id):
    """ Admin only: Ban/Unban users, cleanup records, and notify user """
    if current_user.role != 'admin':
        abort(403)
    
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        flash("You cannot ban another administrator!", "danger")
    else:
        user.is_active = not user.is_active
        
        # If the user is being banned, cleanup their active interactions
        if not user.is_active:
            BloodDonation.query.filter_by(email=user.email, status='Pending').update({'status': 'Cancelled'})
            
            pending_requests = BloodRequest.query.filter_by(requester_email=user.email, status='Pending').all()
            for req in pending_requests:
                donation = BloodDonation.query.filter_by(
                    email=req.donor_email, 
                    blood_groups=req.blood_groups,
                    status='Claimed'
                ).first()
                if donation:
                    donation.status = 'Pending'
                req.status = 'Cancelled'
        
        db.session.commit()
        
        # Send email notification regarding account status
        action = "suspended" if not user.is_active else "reactivated"
        try:
            msg = Message(f"Account {action.capitalize()} - Blood Donation System", 
                          sender=app.config['MAIL_DEFAULT_SENDER'], 
                          recipients=[user.email])
            msg.body = f"Hello {user.username},\n\nYour account has been {action} by an administrator. If you believe this is an error, please contact support."
            mail.send(msg)
        except Exception as e:
            flash("User updated, but email notification failed to send.", "warning")

        status = "banned and their active records cleared" if not user.is_active else "activated"
        flash(f"User {user.username} has been {status}.", "success")
    
    return redirect(url_for('all_users_db'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
    app.run(debug=True)