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
login_manager.login_view = 'login' # Fixed: Points to the login route
login_manager.login_message_category = 'info'

# 2. MODELS
class User(db.Model, UserMixin):
    """ User model for both Admins and regular Donors/Receivers """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False) 
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(10), default='user') # 'admin' or 'user'

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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
        # 1. Fetch user by email (always use .lower() for consistency)
        user = User.query.filter_by(email=form.email.data.lower()).first()

        # 2. Verify if user exists AND password hash matches
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)
            flash(f"Welcome back, {user.username}!", "success")
            
            # Redirect to the page the user was trying to access, or home
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            # Generic error message for security
            flash("Login Unsuccessful. Please check email and password.", "danger")
            
    return render_template('login.html', form=form)

@app.route("/register", methods=['GET', 'POST'])
def register():
    """ Handle new user registration with duplicate check """
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if username or email already exists in the database
        existing_user = User.query.filter(
            (User.username == form.username.data) | 
            (User.email == form.email.data.lower())
        ).first()

        if existing_user:
            flash("Username or Email already registered. Please use different credentials.", "danger")
            return render_template('register.html', form=form)

        # Hash password and save user
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
    """ Register a new donation with pre-filled user data """
    form = DonationForm()

    if request.method == 'GET':
        form.name.data = current_user.username
        form.email.data = current_user.email
    
    if form.validate_on_submit():
        email = form.email.data.lower()
        today = datetime.date.today()
        
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
            donation_counter=(last_entry.donation_counter + 1 if last_entry else 1)
        )
        db.session.add(new_donor)
        db.session.commit()
        flash("Registration successful!", "success")
        return redirect(url_for('home'))
        
    return render_template('donate.html', form=form)

@app.route("/blood_receive", methods=['GET', 'POST'])
@login_required
def blood_receive():
    """ Search for donors based on blood group and city """
    form = RequestForm()
    
    if request.method == 'POST':
        results = BloodDonation.query.filter_by(
            blood_groups=form.blood_groups.data.lower(),
            city=form.city.data.lower()
        ).all()
        
        if not results:
            return render_template('empty_db.html')
            
        return render_template('results.html', 
                               blood_donations=results, 
                               city=form.city.data, 
                               total_result=len(results))
                               
    return render_template('find_blood.html', form=form)

@app.route("/take_donation", methods=['POST'])
@login_required
def take_donation():
    """ Handles the blood request from results.html. """
    donation_id = request.form.get('id')
    donation = BloodDonation.query.get_or_404(donation_id)
    
    requester_email = current_user.email
    
    db.session.delete(donation)
    db.session.commit()
    
    flash(f"Request successful! A notification has been sent to {requester_email}.", "success")
    return redirect(url_for('home'))

@app.route("/all_donations_db")
@login_required
def all_donations_db():
    """ Admin only: View all donation records """
    if current_user.role != 'admin':
        abort(403) 
    donations = BloodDonation.query.all()[::-1]
    count = BloodDonation.query.count()
    return render_template('blood_db.html', blood_donations=donations, all_donations_counter=count)

# 4. CLI COMMANDS
@app.cli.command("create-admin")
def create_admin():
    """ Helper to create an admin via Terminal """
    username = input("Enter admin username: ")
    email = input("Enter admin email: ")
    password = input("Enter admin password: ")
    
    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    admin = User(username=username, email=email, password=hashed_pw, role='admin')
    db.session.add(admin)
    db.session.commit()
    print(f"Admin {username} created successfully!")

if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
    app.run(debug=True)