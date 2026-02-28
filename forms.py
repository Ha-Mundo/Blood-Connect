from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, NumberRange, Length

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