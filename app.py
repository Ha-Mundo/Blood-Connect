import os
import datetime
from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

# Local imports
from forms import DonationForm, RequestForm, RegistrationForm, LoginForm
from time_limit import threshold_donation, threshold_request, is_action_allowed

# 1. INITIALIZATION & CONFIG
load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-very-unsafe')

# Secure Database Path (Instance folder)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'instance', 'BloodDonationSystem.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# 2. MODELS
class User(db.Model, UserMixin):
    """ User model for both Admins and regular Donors/Receivers """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False) 
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(10), default='user')

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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- CONTEXT PROCESSOR FOR STATS ---
@app.context_processor
def inject_global_data():
    """ Inject global stats into all templates (base.html, index.html, etc.) """
    stats = {'donations': 0, 'requests': 0, 'total_available': 0}
    
    # Count all available donations in the system
    stats['total_available'] = BloodDonation.query.count()
    
    if current_user.is_authenticated:
        # User-specific stats
        stats['donations'] = BloodDonation.query.filter_by(email=current_user.email).count()
        stats['requests'] = BloodRequest.query.filter_by(requester_email=current_user.email).count()
        
    return dict(user_stats=stats)

# 3. ROUTES
@app.route("/")
def home():
    """ Main dashboard """
    return render_template('index.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    """ Handle user login with secure password verification """
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
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
        user = User(
            username=form.username.data, 
            email=form.email.data.lower(), 
            password=hashed_pw,
            role='user' 
        )
        db.session.add(user)
        db.session.commit()
        flash("Account created! You can now log in.", "success")
        return redirect(url_for('login'))
        
    return render_template('register.html', form=form)

@app.route("/logout")
@login_required
def logout():
    """ Handle user logout """
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))

@app.route("/blood_donation", methods=['GET', 'POST'])
@login_required
def blood_donation():
    """ Register a new donation or view current pending donation """
    
    # Check if the user already has a pending donation
    active_donation = BloodDonation.query.filter_by(email=current_user.email, status='Pending').first()
    
    form = DonationForm()
    if request.method == 'GET':
        form.name.data = current_user.username
        form.email.data = current_user.email
    
    # Only process form if there is no active donation
    if form.validate_on_submit() and not active_donation:
        email = form.email.data.lower()
        today = datetime.date.today()
        # 90 days check
        last_entry = BloodDonation.query.filter_by(email=email).order_by(BloodDonation.id.desc()).first()
        if last_entry and not is_action_allowed(last_entry.next_donation, today):
            flash("Safety limit: You can only donate once every 90 days.", "danger")
            return redirect(url_for('blood_donation'))

        new_donor = BloodDonation(
            name=form.name.data.lower(), 
            age=form.age.data,
            blood_groups=form.blood_groups.data.lower(), 
            city=form.city.data.lower(),
            email=email, 
            latest_donation=today, 
            next_donation=threshold_donation(today),
            donation_counter=(last_entry.donation_counter + 1 if last_entry else 1),
            status='Pending' # Explicitly set status
        )
        db.session.add(new_donor)
        db.session.commit()
        flash("Registration successful!", "success")
        # Redirect back to the same page to show the pending status
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
    """ Search for donors based on blood group and city with pagination """
    form = RequestForm()
    
    # Get parameters from POST (initial search) or GET (pagination links)
    city = request.form.get('city') or request.args.get('city')
    bg = request.form.get('blood_groups') or request.args.get('bg')
    
    if city and bg:
        # Get current page number from URL, default is 1
        page = request.args.get('page', 1, type=int)
        
        # Query with pagination (10 items per page)
        pagination = BloodDonation.query.filter_by(
            blood_groups=bg.lower(),
            city=city.lower()
        ).paginate(page=page, per_page=10, error_out=False)
        
        if not pagination.items:
            return render_template('empty_db.html')
            
        return render_template('results.html', 
                               pagination=pagination, 
                               city=city, 
                               bg=bg)
                               
    return render_template('find_blood.html', form=form)

@app.route("/take_donation", methods=['POST'])
@login_required
def take_donation():
    donation_id = request.form.get('id')
    donation = BloodDonation.query.get_or_404(donation_id)
    today = datetime.date.today()

    # --- PREVENT SELF-REQUEST ---
    if donation.email == current_user.email:
        flash("You cannot request your own donation!", "warning")
        return redirect(url_for('home'))

    # --- 7 DAYS REQUEST LIMIT ---
    last_request = BloodRequest.query.filter_by(requester_email=current_user.email).order_by(BloodRequest.id.desc()).first()
    if last_request:
        # We calculate the allowed date for the next request
        allowed_date = threshold_request(last_request.request_date)
        if not is_action_allowed(allowed_date, today):
            flash("Safety limit: You can only make one request every 7 days.", "danger")
            return redirect(url_for('home'))
    
    # Process request
    new_request = BloodRequest(
        name=current_user.username.lower(),
        blood_groups=donation.blood_groups,
        city=donation.city,
        requester_email=current_user.email,  
        donor_email=donation.email,          
        request_date=today)
    
    db.session.add(new_request)
    db.session.delete(donation)
    db.session.commit()
    
    flash(f"Request successful! Notification sent.", "success")
    return redirect(url_for('home'))

@app.route("/all_donations_db")
@login_required
def all_donations_db():
    """ Admin only: View all donation records paginated """
    if current_user.role != 'admin':
        abort(403) 
        
    page = request.args.get('page', 1, type=int)
    # Paginate all records ordered by newest first
    pagination = BloodDonation.query.order_by(BloodDonation.id.desc()).paginate(page=page, per_page=10, error_out=False)
    count = BloodDonation.query.count()
    
    return render_template('donation_db.html', pagination=pagination, all_donations_counter=count)

@app.route("/all_requests_db")
@login_required
def all_requests_db():
    """ Admin only: View all request records paginated """
    if current_user.role != 'admin':
        abort(403) 
        
    page = request.args.get('page', 1, type=int)
    # Paginate all records ordered by newest first
    pagination = BloodRequest.query.order_by(BloodRequest.id.desc()).paginate(page=page, per_page=10, error_out=False)
    count = BloodRequest.query.count()
    
    return render_template('request_db.html', pagination=pagination, all_requests_counter=count)

if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
    app.run(debug=True)