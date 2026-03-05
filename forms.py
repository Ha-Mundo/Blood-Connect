from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email, Length

# English: Predefined list for the dropdown menus
BLOOD_CHOICES = [
    ('A+', 'A+'), ('A-', 'A-'), 
    ('B+', 'B+'), ('B-', 'B-'), 
    ('AB+', 'AB+'), ('AB-', 'AB-'), 
    ('O+', 'O+'), ('O-', 'O-')
]

class RegistrationForm(FlaskForm):
    """ Form for new user registration """
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    """ Form for user login using Email """
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class DonationForm(FlaskForm):
    """ Form for registering a donation with Dropdown """
    name = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    age = IntegerField('Age', validators=[DataRequired()])
    blood_groups = SelectField('Blood Group', choices=BLOOD_CHOICES, validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    submit = SubmitField('Confirm Donation')

class RequestForm(FlaskForm):
    """ Form for searching donors with Dropdown """
    name = StringField('Recipient Name')
    email = StringField('Your Contact Email')
    blood_groups = SelectField('Blood Group', choices=BLOOD_CHOICES, validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    submit = SubmitField('Search Donors')