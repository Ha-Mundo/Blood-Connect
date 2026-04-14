import uuid
from types import SimpleNamespace
from datetime import date

from app.models import User, BloodDonation
from app.services.blood_service import BloodService
from app.extensions import bcrypt


def make_user(**kwargs):
    return User(
        username=kwargs.get("username", "test_user"),
        email=kwargs.get("email", f"test_{uuid.uuid4()}@example.com"),
        password=bcrypt.generate_password_hash(
            kwargs.get("password", "Password1!")
        ).decode("utf-8"),
        blood_group=kwargs.get("blood_group", "o+"),
        is_active=kwargs.get("is_active", True),
        is_verified=kwargs.get("is_verified", True),
        role=kwargs.get("role", "user"),
    )


def make_donation_form(**kwargs):
    return SimpleNamespace(
        name=SimpleNamespace(data=kwargs.get("name", "Test User")),
        email=SimpleNamespace(data=kwargs.get("email", "test@example.com")),
        age=SimpleNamespace(data=kwargs.get("age", 30)),
        blood_groups=SimpleNamespace(data=kwargs.get("blood_groups", "O+")),
        city=SimpleNamespace(data=kwargs.get("city", "Rome")),
    )


def test_create_donation_rejects_underage(app, db_session):
    with app.app_context():
        user = make_user()
        form = make_donation_form(email=user.email, age=17)

        donation, error = BloodService.create_donation(
            form=form,
            user=user,
            latest_donation=None,
            today=date.today()
        )

        assert donation is None
        assert error == "Legal requirement: You must be at least 18 years old to donate blood."


def test_create_donation_success(app, db_session):
    with app.app_context():
        user = make_user()
        form = make_donation_form(email=user.email, name="Test User", blood_groups="O+", city="Rome")

        donation, error = BloodService.create_donation(
            form=form,
            user=user,
            latest_donation=None,
            today=date.today()
        )

        assert error is None
        assert donation is not None
        assert donation.email == user.email
        assert donation.status == "Pending"
        
        
def test_take_donation_prevents_self_request(app, db_session):
    with app.app_context():
        user = make_user(email="user@example.com")

        donation = BloodDonation(
            name="user",
            age=30,
            blood_groups="o+",
            city="rome",
            email=user.email,  # stesso utente → deve bloccare
            latest_donation=date.today(),
            next_donation=date.today(),
            donation_counter=1,
            status="Approved"
        )

        db_session.add(donation)
        db_session.commit()

        result, error = BloodService.take_donation(
            donation=donation,
            user=user
        )

        assert result is None
        assert error == "You cannot request your own donation!"