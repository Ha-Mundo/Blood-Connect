import uuid
import pytest
from app import create_app
from app.extensions import db
from app.models import User
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()


@pytest.fixture
def user():
    return User(
        username="test",
        email=f"test_{uuid.uuid4()}@example.com",
        password=bcrypt.generate_password_hash("Password1!").decode("utf-8"),
        is_active=True,
        is_verified=True
    )


@pytest.fixture(scope="session")
def app():
    app = create_app()

    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        WTF_CSRF_ENABLED=False,
    )

    return app


@pytest.fixture(scope="function")
def db_session(app):
    with app.app_context():
        db.create_all()

        connection = db.engine.connect()
        transaction = connection.begin()

        # bind session to connection
        session = db.session
        session.bind = connection

        yield session

        session.rollback()
        transaction.rollback()
        connection.close()
        session.remove()

        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()