from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Email, Length

class RegistrationForm(FlaskForm):
    """ Form for new user registration """
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    """ Form for user login - Updated to use Email """
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class DonationForm(FlaskForm):
    """ Form for registering a donation """
    name = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    age = IntegerField('Age', validators=[DataRequired()])
    blood_groups = StringField('Blood Group', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    submit = SubmitField('Confirm Donation')

class RequestForm(FlaskForm):
    """ Form for searching donors """
    name = StringField('Recipient Name')
    email = StringField('Your Contact Email')
    blood_groups = StringField('Blood Group', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    submit = SubmitField('Search Donors')