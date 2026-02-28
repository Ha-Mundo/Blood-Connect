import os
import datetime
from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

# Local imports
from forms import DonationForm, RequestForm
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

# 2. MODELS (Keeping them here for simplicity, but could be in models.py)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False) 
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(10), default='user') # 'admin' or 'user'

class BloodDonation(db.Model):
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

# 3. PUBLIC ROUTES (Home, Donate, Find)
@app.route("/")
def home():
    return render_template('index.html')

@app.route("/blood_donation", methods=['GET', 'POST'])
def blood_donation():
    form = DonationForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        today = datetime.date.today()
        
        last_entry = BloodDonation.query.filter_by(email=email).order_by(BloodDonation.id.desc()).first()
        if last_entry and not is_action_allowed(last_entry.next_donation, today):
            flash("Safety limit: You can only donate once every 90 days.", "danger")
            return redirect(url_for('blood_donation'))

        new_donor = BloodDonation(
            name=form.name.data.lower(), age=form.age.data,
            blood_groups=form.blood_groups.data.lower(), city=form.city.data.lower(),
            email=email, latest_donation=today, 
            next_donation=threshold_donation(today),
            donation_counter=(last_entry.donation_counter + 1 if last_entry else 1)
        )
        db.session.add(new_donor)
        db.session.commit()
        flash("Registration successful! Thank you for your donation.", "success")
        return redirect(url_for('home'))
    return render_template('donate.html', form=form)

@app.route("/blood_receive", methods=['GET', 'POST'])
def blood_receive():
    form = RequestForm()
    if form.validate_on_submit():
        results = BloodDonation.query.filter_by(
            blood_groups=form.blood_groups.data.lower(),
            city=form.city.data.lower()
        ).all()
        
        if not results:
            return render_template('empty_db.html')
        return render_template('results.html', blood_donations=results, city=form.city.data, total_result=len(results))
    return render_template('find_blood.html', form=form)

# 4. ADMIN & AUTH ROUTES
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('all_donations_db'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and bcrypt.check_password_hash(user.password, request.form.get('password')):
            login_user(user)
            return redirect(url_for('all_donations_db'))
        flash("Invalid credentials. Access denied.", "danger")
    return render_template('login.html')

@app.route("/all_donations_db")
@login_required
def all_donations_db():
    if current_user.role != 'admin':
        abort(403) # Forbidden: The user logged in does not have permissions
    donations = BloodDonation.query.all()[::-1]
    count = BloodDonation.query.count()
    return render_template('blood_db.html', blood_donations=donations, all_donations_counter=count)

@app.route("/take_donation", methods=['POST'])
@login_required # Only admin can remove records in this version
def take_donation():
    donation_id = request.form.get('id')
    donation = BloodDonation.query.get_or_404(donation_id)
    db.session.delete(donation)
    db.session.commit()
    flash("Record removed successfully.", "success")
    return redirect(url_for('all_donations_db'))

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.cli.command("create-admin")
def create_admin():
    """Custom command to create an admin user from terminal."""
    username = input("Enter admin username: ")
    password = input("Enter admin password: ")
    
    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    admin = User(username=username, password=hashed_pw)
    # is_admin=True 
    db.session.add(admin)
    db.session.commit()
    print(f"Admin {username} created successfully!")

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Ensure DB tables exist
    app.run(debug=True)