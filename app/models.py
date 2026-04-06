""" Database models definition """
import datetime
from flask_login import UserMixin
from app.extensions import db

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False) 
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(10), default='user')
    blood_group = db.Column(db.String(5), nullable=True)
    is_verified = db.Column(db.Boolean, nullable=False, default=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

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
    status = db.Column(db.String(20), nullable=False, default='Pending')

class BloodRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    blood_groups = db.Column(db.String(5), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    requester_email = db.Column(db.String(120), nullable=False)  
    donor_email = db.Column(db.String(120), nullable=False)     
    request_date = db.Column(db.Date, nullable=False, default=datetime.date.today)
    status = db.Column(db.String(20), nullable=False, default='Pending')