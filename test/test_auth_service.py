import uuid
import pytest
from app.services.auth_service import AuthService
from app.models import User
from app.extensions import bcrypt


def create_user(email=None, password="Password1!", is_active=True, is_verified=True):
    return User(
        username="test_user",
        email=email or f"test_{uuid.uuid4()}@example.com",
        password=bcrypt.generate_password_hash(password).decode("utf-8"),
        is_active=is_active,
        is_verified=is_verified,
    )


def unpack(result):
    """
    AuthService returns:
    (user, error) or (None, error)
    """
    if isinstance(result, tuple):
        return result
    return result, None


# -------------------
# LOGIN SUCCESS
# -------------------
def test_authenticate_success(app, db_session):
    with app.app_context():
        user = create_user()
        db_session.add(user)
        db_session.commit()

        result, error = AuthService.authenticate(
            email=user.email,
            password="Password1!"
        )

        assert error is None
        assert result is not None
        assert result.email == user.email


# -------------------
# LOGIN FAIL (wrong password)
# -------------------
def test_authenticate_wrong_password(app, db_session):
    with app.app_context():
        user = create_user()
        db_session.add(user)
        db_session.commit()

        result, error = AuthService.authenticate(
            email=user.email,
            password="WrongPassword!"
        )

        assert result is None
        assert error == "Invalid credentials"


# -------------------
# LOGIN FAIL (inactive user)
# -------------------
def test_authenticate_inactive_user(app, db_session):
    with app.app_context():
        user = create_user(is_active=False)
        db_session.add(user)
        db_session.commit()

        result, error = AuthService.authenticate(
            email=user.email,
            password="Password1!"
        )

        assert result is None
        assert error == "Account disabled"


# -------------------
# LOGIN FAIL (unverified user)
# -------------------
def test_authenticate_unverified_user(app, db_session):
    with app.app_context():
        user = create_user(is_verified=False)
        db_session.add(user)
        db_session.commit()

        result, error = AuthService.authenticate(
            email=user.email,
            password="Password1!"
        )

        assert result is None
        assert error == "Email not verified"


# -------------------
# LOGIN FAIL (user not found)
# -------------------
def test_authenticate_user_not_found(app, db_session):
    with app.app_context():
        result, error = AuthService.authenticate(
            email="notfound@example.com",
            password="Password1!"
        )

        assert result is None
        assert error == "Invalid credentials"


# -------------------
# RESET PASSWORD (success)
# -------------------
def test_reset_password(app, db_session):
    with app.app_context():
        user = create_user(password="OldPassword1!")
        db_session.add(user)
        db_session.commit()

        result = AuthService.reset_password(
            email=user.email,
            new_password="NewPassword1!"
        )

        assert result is None  # service returns None on success


# -------------------
# RESET PASSWORD + AUTH CHECK
# -------------------
def test_reset_password_and_authenticate(app, db_session):
    with app.app_context():
        user = create_user(password="OldPassword1!")
        db_session.add(user)
        db_session.commit()

        AuthService.reset_password(
            email=user.email,
            new_password="NewPassword1!"
        )

        result, error = AuthService.authenticate(
            email=user.email,
            password="NewPassword1!"
        )

        assert error is None
        assert result is not None


# -------------------
# RESET PASSWORD (invalid password)
# -------------------
def test_reset_password_invalid_password(app, db_session):
    with app.app_context():
        user = create_user()
        db_session.add(user)
        db_session.commit()

        result = AuthService.reset_password(
            email=user.email,
            new_password="123"
        )

        assert result is None


# -------------------
# RESET PASSWORD (user not found)
# -------------------
def test_reset_password_user_not_found(app, db_session):
    with app.app_context():
        result = AuthService.reset_password(
            email="missing@example.com",
            new_password="NewPassword1!"
        )

        assert result == "Invalid user"