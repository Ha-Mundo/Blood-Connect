from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, NumberRange, Length

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Sign Up')

class DonationForm(FlaskForm):
    # Field for Name with length validation to prevent Buffer Overflow attempts
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=50)])
    
    # Integer field with range to ensure data integrity
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=18, max=70)])
    
    # SelectField prevents users from injecting custom/malicious blood groups
    blood_groups = SelectField('Blood Group', choices=[
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')
    ])
    
    city = StringField('City', validators=[DataRequired(), Length(max=50)])
    
    # Email validator ensures the input follows the correct format
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    
    submit = SubmitField('Submit Donation')
    
class RequestForm(FlaskForm):
    name = StringField('Recipient Name', validators=[DataRequired(), Length(min=2, max=50)])
    blood_groups = SelectField('Blood Group Needed', choices=[
        ('a+', 'A+'), ('a-', 'A-'), ('b+', 'b+'), ('b-', 'B-'),
        ('ab+', 'AB+'), ('ab-', 'AB-'), ('o+', 'O+'), ('o-', 'O-')
    ])
    city = StringField('City', validators=[DataRequired(), Length(max=50)])
    email = StringField('Your Contact Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Search for Donors')