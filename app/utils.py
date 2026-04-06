""" Centralized utility functions """
from itsdangerous import URLSafeTimedSerializer
from flask import current_app

def generate_confirmation_token(email):
    """ Generate a secure, time-sensitive token for email verification """
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='email-confirm-salt')