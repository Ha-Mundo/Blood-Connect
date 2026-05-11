import uuid
from types import SimpleNamespace
from datetime import date

from app.extensions import bcrypt
from app.models import User, BloodDonation, BloodRequest
from app.services.main_service import MainService


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


def test_update_profile_changes_username_blood_group_and_password(app, db_session):
    with app.app_context():
        user = make_user(username="old_name", blood_group="a+")
        db_session.add(user)
        db_session.commit()

        form = SimpleNamespace(
            username=SimpleNamespace(data="New Name"),
            blood_group=SimpleNamespace(data="b-"),
            new_password=SimpleNamespace(data="NewPassword1!"),
            email_notifications=SimpleNamespace(data=True)
        )

        MainService.update_profile(user, form)

        refreshed = User.query.filter_by(email=user.email).first()
        assert refreshed.username == "new name"
        assert refreshed.blood_group == "b-"
        assert bcrypt.check_password_hash(refreshed.password, "NewPassword1!")


def test_get_global_stats_counts_completed_activity(app, db_session):
    with app.app_context():
        user = make_user(email="user@example.com")
        db_session.add(user)

        db_session.add(BloodDonation(
            name="donor",
            age=30,
            blood_groups="o+",
            city="rome",
            email="donor@example.com",
            latest_donation=date.today(),
            next_donation=date.today(),
            donation_counter=1,
            status="Approved",
        ))

        db_session.add(BloodDonation(
            name="user",
            age=30,
            blood_groups="o+",
            city="rome",
            email=user.email,
            latest_donation=date.today(),
            next_donation=date.today(),
            donation_counter=1,
            status="Completed",
        ))

        db_session.add(BloodRequest(
            name="user",
            blood_groups="o+",
            city="rome",
            requester_email=user.email,
            donor_email="donor@example.com",
            request_date=date.today(),
            status="Completed",
        ))

        db_session.commit()

        fake_current_user = SimpleNamespace(is_authenticated=True, email=user.email, email_notifications=True)
        stats = MainService.get_global_stats(fake_current_user)

        assert stats["total_available"] == 1
        assert stats["donations"] == 1
        assert stats["requests"] == 1