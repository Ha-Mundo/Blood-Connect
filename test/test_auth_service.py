
import pytest
from app.services.auth_service import AuthService
from app.models import User
from app.extensions import bcrypt

def create_user(db_session, User, bcrypt, **kwargs):
    user = User(
        username=kwargs.get("username", "testuser"),
        email=kwargs.get("email", "test@example.com"),
        password=bcrypt.generate_password_hash("Password1!").decode('utf-8'),
        is_active=kwargs.get("is_active", True),
        is_verified=kwargs.get("is_verified", True)
    )
    db_session.add(user)
    db_session.commit()
    return user


def test_authenticate_success(app, db_session, user):
    db_session.add(user)
    db_session.commit()
    
# -------------------
# LOGIN SUCCESS
# -------------------
def test_authenticate_success(app, db_session):
    with app.app_context():
        user = User(
            username="test",
            email="test@example.com",
            password=bcrypt.generate_password_hash("Password1!").decode('utf-8'),
            is_active=True,
            is_verified=True
        )
        db_session.add(user)
        db_session.commit()

        result, error = AuthService.authenticate("test@example.com", "Password1!")

        assert result is not None
        assert error is None


# -------------------
# LOGIN FAIL (wrong password)
# -------------------
def test_authenticate_wrong_password(app, db_session):
    with app.app_context():
        user = User(
            username="test",
            email="test@example.com",
            password=bcrypt.generate_password_hash("Password1!").decode('utf-8'),
            is_active=True,
            is_verified=True
        )
        db_session.add(user)
        db_session.commit()

        result, error = AuthService.authenticate("test@example.com", "WrongPass!")

        assert result is None
        assert error == "Invalid credentials"


# -------------------
# LOGIN FAIL (inactive user)
# -------------------
def test_authenticate_inactive_user(app, db_session):
    with app.app_context():
        user = User(
            username="test",
            email="test@example.com",
            password=bcrypt.generate_password_hash("Password1!").decode('utf-8'),
            is_active=False,
            is_verified=True
        )
        db_session.add(user)
        db_session.commit()

        result, error = AuthService.authenticate("test@example.com", "Password1!")

        assert result is None
        assert error == "Account disabled"


# -------------------
# RESET PASSWORD
# -------------------
def test_reset_password(app, db_session):
    with app.app_context():
        user = User(
            username="test",
            email="test@example.com",
            password=bcrypt.generate_password_hash("Password1!").decode('utf-8'),
            is_active=True,
            is_verified=True
        )
        db_session.add(user)
        db_session.commit()

        error = AuthService.reset_password("test@example.com", "NewPassword1!")

        assert error is None

        updated_user = User.query.filter_by(email="test@example.com").first()
        assert bcrypt.check_password_hash(updated_user.password, "NewPassword1!")