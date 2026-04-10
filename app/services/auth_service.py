from flask import current_app, url_for
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from app.extensions import db, bcrypt
from app.models import User
from app.security import generate_confirmation_token


class AuthService:

    @staticmethod
    def authenticate(email, password):
        user = User.query.filter_by(email=email.lower()).first()

        if not user or not bcrypt.check_password_hash(user.password, password):
            return None, "Invalid credentials"

        if not user.is_active:
            return None, "Account disabled"

        if not user.is_verified:
            return None, "Email not verified"

        return user, None

    @staticmethod
    def register(username, email, password):
        existing_user = User.query.filter(
            (User.username == username) |
            (User.email == email.lower())
        ).first()

        if existing_user:
            return None, "User already exists"

        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

        user = User(
            username=username,
            email=email.lower(),
            password=hashed_pw
        )

        db.session.add(user)
        db.session.commit()

        return user, None

    @staticmethod
    def generate_email_token(email):
        return generate_confirmation_token(email, 'email-confirm')

    @staticmethod
    def generate_reset_token(email):
        return generate_confirmation_token(email, 'password-reset')

    @staticmethod
    def verify_token(token, salt, max_age):
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

        try:
            email = serializer.loads(token, salt=salt, max_age=max_age)
            return email, None
        except (BadSignature, SignatureExpired):
            return None, "Invalid or expired token"

    @staticmethod
    def confirm_user(email):
        user = User.query.filter_by(email=email).first()

        if not user:
            return None, "Invalid token"

        if not user.is_verified:
            user.is_verified = True
            db.session.commit()

        return user, None

    @staticmethod
    def reset_password(email, new_password):
        user = User.query.filter_by(email=email).first()

        if not user or not user.is_active:
            return "Invalid user"

        hashed_pw = bcrypt.generate_password_hash(new_password).decode('utf-8')
        user.password = hashed_pw
        db.session.commit()

        return None