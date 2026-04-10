""" Centralized utility functions """
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from urllib.parse import urlparse, urljoin

""" def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='email-confirm-salt') """

def generate_confirmation_token(email, salt):
    """ Generate a secure, time-sensitive token for email verification """
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=salt)


def is_safe_url(target, host_url):
    ref_url = urlparse(host_url)
    test_url = urlparse(urljoin(host_url, target))
    return (
        test_url.scheme in ("http", "https") and
        ref_url.netloc == test_url.netloc
    )