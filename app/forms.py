from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp, Optional

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
    password = PasswordField('Password', validators=[
        DataRequired(), 
        Length(min=8, message="Password must be at least 8 characters long."),
        # Add Regexp validator for complexity
        Regexp(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[\W_]).+$', 
               message="Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character.")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), 
        EqualTo('password', message='Passwords must match. Please try again.')
    ])
    submit = SubmitField('Sign in')

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
    
class ForgotPasswordForm(FlaskForm):
    # Form to request password reset
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    # Form to enter new password
    password = PasswordField('New Password', validators=[
        DataRequired(), 
        Length(min=8),
        Regexp(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[\W_]).+$', 
               message="Password must contain uppercase, lowercase, number, and special character.")
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(), 
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Reset Password')
    
class ProfileForm(FlaskForm):
    """ Form for updating user profile """
    username = StringField('Full Name', validators=[Optional(), Length(min=2, max=50)])
    blood_group = SelectField('Blood Group', choices=[('', 'Select Blood Group...')] + BLOOD_CHOICES, validators=[Optional()])
    
    new_password = PasswordField('New Password', validators=[
        Optional(), 
        Length(min=8),
        Regexp(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[\W_]).+$', 
               message="Password must contain uppercase, lowercase, number, and special character.")
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        EqualTo('new_password', message='Passwords must match.')
    ])
    
    email_notifications = BooleanField("Email Notifications")
    
    submit = SubmitField('Update Profile')