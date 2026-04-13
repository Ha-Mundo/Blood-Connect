import uuid
import pytest

from app.models import User
from app.extensions import bcrypt
from app.services.admin_service import AdminService


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


def test_get_users_page_filters_by_search_and_verified(app, db_session):
    with app.app_context():
        alice = make_user(username="Alice", email="alice@example.com", is_verified=True)
        bob = make_user(username="Bob", email="bob@example.com", is_verified=False)

        db_session.add_all([alice, bob])
        db_session.commit()

        pagination, count = AdminService.get_users_page(
            page=1,
            search="alice",
            verified="1"
        )

        assert count == 1
        assert len(pagination.items) == 1
        assert pagination.items[0].email == "alice@example.com"


def test_build_csv_invalid_table_type_raises_value_error():
    with pytest.raises(ValueError):
        AdminService.build_csv("unknown")
       

def test_toggle_user_changes_active_status(app, db_session):
    with app.app_context():
        user = make_user(is_active=True)

        db_session.add(user)
        db_session.commit()

        updated_user, message = AdminService.toggle_user(user)

        assert updated_user.is_active is False
        assert "banned" in message.lower()


def test_toggle_user_prevents_admin_ban(app, db_session):
    with app.app_context():
        admin = make_user(role="admin")

        db_session.add(admin)
        db_session.commit()

        updated_user, message = AdminService.toggle_user(admin)

        assert updated_user.is_active is True
        assert "cannot ban" in message.lower() 