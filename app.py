"""
TODO 
add pagination
improve ui
"""

import os
from flask import Flask, request, jsonify, render_template, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import datetime
from time_limit import threshold_donation, threshold_request
from flask_wtf.csrf import CSRFProtect
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from forms import DonationForm

# Loading environment variables
load_dotenv()

app = Flask(__name__)

# If the environment variable doesn't exist, we use a fallback (dev only!)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-dev-key-molto-insicura')

# We correctly point to the 'instance' folder
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'BloodDonationSystem.db')
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize protection against Cross-Site Request Forgery attacks
csrf = CSRFProtect(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' # Redirect here if unauthorized
login_manager.login_message_category = 'info'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False) # Will store the hashed password
    
    def __init__(self, username, password):
        self.name = username
        self.password = password
    
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


    def __init__(self, name, age, blood_groups, city, email, latest_donation, next_donation, donation_counter):
        self.name = name
        self.age = age
        self.blood_groups = blood_groups
        self.city = city
        self.email = email
        self.latest_donation = latest_donation
        self.next_donation = next_donation
        self.donation_counter = donation_counter
        
class BloodRequest(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable=False)
    blood_groups = db.Column(db.String(5), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    latest_request = db.Column(db.Date, nullable=False)
    next_request = db.Column(db.Date)
    request_counter = db.Column(db.Integer, default=1)


    def __init__(self, name, blood_groups, city, email, latest_request, next_request, request_counter):
        self.name = name
        self.blood_groups = blood_groups
        self.city = city
        self.email = email
        self.latest_request = latest_request
        self.next_request = next_request
        self.request_counter = request_counter
        
@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Secure login route for administrators.
    Uses Bcrypt for hash verification to prevent credential exposure.
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        # Security: Verify user exists and check password hash
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash("Login successful! Welcome back, Admin.", "success")
            return redirect(url_for('all_donations_db'))
        else:
            # Security Tip: Use a generic error message to prevent 'Username Enumeration'
            flash("Login failed. Check your credentials and try again.", "danger")
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out safely.", "info")
    return redirect(url_for('home'))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/empty_db')
def no_donations():
    return render_template('empty_db.html')

@app.route('/blood_donation', methods=['GET', 'POST'])
def blood_donation():
    """
    Handles new blood donation submissions.
    Security: Automatic CSRF protection and Server-Side validation via Flask-WTF.
    """
    form = DonationForm()
    
    # validate_on_submit() checks if the request is POST AND if the CSRF token is valid
    if form.validate_on_submit():
        # Get cleaned and validated data from the form
        email = form.email.data.lower()
        
        # Check if the donor already exists to verify the 3-month threshold
        existing_donor = BloodDonation.query.filter_by(email=email).order_by(BloodDonation.id.desc()).first()
        today = datetime.date.today()

        if existing_donor:
            # Check if the 'next_donation' date has passed
            if existing_donor.next_donation > today:
                flash("Donation forbidden! Only one blood donation every 3 months is allowed.", "danger")
                return redirect(url_for('blood_donation'))
            
            # Increment counter for returning donors
            counter = existing_donor.donation_counter + 1
        else:
            counter = 1

        # Create new record using validated data
        new_donation = BloodDonation(
            name=form.name.data.lower(),
            age=form.age.data,
            blood_groups=form.blood_groups.data.lower(),
            city=form.city.data.lower(),
            email=email,
            latest_donation=today,
            next_donation=threshold_donation(today),
            donation_counter=counter
        )

        try:
            db.session.add(new_donation)
            db.session.commit()
            flash(f"Thank you {form.name.data.capitalize()} for your availability. We'll get in touch soon!", "success")
            return redirect(url_for('home'))
        except Exception as e:
            db.session.rollback()
            flash("A database error occurred. Please try again later.", "warning")
            return redirect(url_for('blood_donation'))

    # If it's a GET request or form validation fails
    return render_template('donate.html', form=form)

@app.route('/blood_receive', methods=['GET','POST'])
def blood_receive():
    if request.method == 'GET':

        all_donations = BloodDonation.query.all()
        if all_donations == []:
            print('Sorry no donations available')
            return render_template('empty_db.html')

        blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        return render_template('find_blood.html', blood_groups = blood_groups)

    else:
        blood_groups = request.form.get('blood_groups').lower()
        city = request.form.get('city').lower()
        name = request.form.get('name').lower()
        email = request.form.get('email').lower()
        
        if city == "":
            return "Please enter all the details." 
        
        next_request_date = threshold_request(donation_day)
        receiver_fields = ['blood_groups','city','name','email']
    
        request_dict = {}
        request_dict['latest_request'] = donation_day
        request_dict['next_request'] = next_request_date
        
        for field in receiver_fields:
            request_dict[field] = request.form.get(field).lower()
            
        counter = db.session.query(BloodRequest).filter(BloodRequest.email == request_dict['email']).count() 
        next_br = db.session.query(BloodRequest).filter(BloodRequest.next_request).count()
        
        if counter == 0:
            counter += 1
            request_dict['request_counter'] = counter
            blood_request = BloodRequest(**request_dict)
            db.session.add(blood_request)
            db.session.commit()
           
        elif next_br > 0:
            query = db.session.query(BloodRequest.next_request).filter(BloodRequest.email == request_dict['email']).all()
            next_br_date = list(query[::-1][0])
            
            if next_br_date[0] <= donation_day:   
                counter += 1
                request_dict['request_counter'] = counter
                blood_request = BloodRequest(**request_dict)
                db.session.add(blood_request)
                db.session.commit()
                
            else:
                flash("Request Forbidden! Is allowed only one blood request per week", "danger")   
                return redirect(url_for('blood_receive')) 
            
        else:
            flash("Request Forbidden!!! Is allowed only one blood request per week", "danger")   
            return redirect(url_for('blood_receive'))  
    
   
        print(city, blood_groups)
        result = BloodDonation.query\
            .filter_by(blood_groups = blood_groups)\
            .filter_by(city = city)\
            .all()
                
        total_result = BloodDonation.query\
            .filter_by(blood_groups = blood_groups)\
            .filter_by(city = city)\
            .count()
        
        if result == []:
            print('Sorry no donations available')
            return render_template('empty_db.html')
        else:
            return render_template('results.html', blood_donations=result, city=city, total_result = total_result)
        
    print(result)
    return render_template('results.html', blood_donations=result)

@app.route('/take_donation', methods=['POST'])
def take_donation():
    """
    Handles the deletion of a blood donation record.
    Security Improvements:
    1. Changed from GET to POST to prevent CSRF (Cross-Site Request Forgery).
    2. Added email verification to mitigate IDOR (Insecure Direct Object Reference).
    3. Uses get_or_404 for robust error handling.
    """
    
    # Retrieve data from the secure POST form
    blood_donation_id = request.form.get('id')
    user_email = request.form.get('email', '').lower()

    # 1. Validation: Ensure both fields are provided
    if not blood_donation_id or not user_email:
        flash("Invalid request. Please provide all required information.", "danger")
        return redirect(url_for('all_donations_db'))

    # 2. Fetch the record or return a 404 error if not found (Prevents app crashes)
    donation = BloodDonation.query.get_or_404(blood_donation_id)

    # 3. Security Check: Only the owner (by email) can delete their donation
    # This prevents an attacker from deleting random records by guessing IDs
    if donation.email != user_email:
        # Log this internally as a potential suspicious activity
        flash("Access Denied! You are not authorized to remove this record.", "danger")
        return redirect(url_for('all_donations_db'))

    try:
        # 4. Perform the deletion
        db.session.delete(donation)
        db.session.commit()
        
        # Success message for the user
        flash("Donation record successfully processed. Thank you for your contribution!", "success")
    except Exception as e:
        # Handle database errors gracefully
        db.session.rollback()
        flash("An error occurred while processing your request. Please try again later.", "warning")
    
    return redirect(url_for('home'))

@app.route('/all_donations_db', methods=['GET'])
@login_required # Only a logged admin can see this page
def all_donations_db():
    """
    Administrative view. Only accessible by authorized super-users.
    """
    all_donations = BloodDonation.query.all()[::-1]
    all_donations_counter = BloodDonation.query.count()
    return render_template('blood_db.html', 
                           blood_donations=all_donations, 
                           all_donations_counter=all_donations_counter)

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(debug=False)