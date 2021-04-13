import pytest

from config import settings
from snake_eyes.app import create_app
from snake_eyes.extensions import db as _db
from snake_eyes.blueprints.user.models import User


@pytest.fixture(scope="session")
def app():
    """
    Setup a test app for snake_eyes.
    Session scopes makes it live for the entire duration of the test.

    :return: snake_eyes app
    """
    params = {
        "DEBUG": False,
        "WTF_CSRF_ENABLED": False,
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"{settings.SQLALCHEMY_DATABASE_URI}_test"
    }
    test_app = create_app(settings_override=params)

    with test_app.app_context():
        yield test_app


@pytest.fixture(scope="function")
def client(app):
    """
    Setup a test client from the snake_eyes app.
    This is created for every test function run to provide isolation.

    :param app: Pytest app fixture
    :return: snake_eyes app test client
    """
    yield app.test_client()


@pytest.fixture(scope="session")
def db(app):
    """
    Setup a db for testing.
    Session scopes makes it live for the entire duration of the test.

    :param app: Pytest app fixture
    :return: SQLAlchemy database session
    """
    _db.drop_all()
    _db.create_all()

    params = {
        "role": "admin",
        "email": "admin@localhost",
        "password": "password"
    }

    admin = User(**params)

    _db.session.add(admin)
    _db.session.commit()

    return _db


@pytest.fixture(scope="function")
def session(db):
    """
    Speeds up testing using rollbacks and nested session.
    Requires the DB to support SQL savepoints.
    This is created for every test function run to provide isolation.

    :param db: Pytest db fixture
    """
    db.session.begin_nested()

    yield db.session

    db.session.rollback()


@pytest.fixture(scope="session")
def token(db):
    """
    Serialize a JWS token
    Session scopes makes it live for the entire duration of the test.

    :param db: Pytest db fixture
    :return: JWS Token
    """
    user = User.find_by_identity("admin@localhost")

    return user.serialize_token()


@pytest.fixture(scope="function")
def users(db):
    """
    Create user fixtures.
    This is created for every test function run to provide isolation.

    :param db: Pytest db fixture
    :return: SQLAlchemy database session
    """

    db.session.query(User).delete()

    users = [
        {"role": "admin", "email": "admin@localhost", "password": "password"},
        {"active": False, "email": "disabl@localhost", "password": "password"}
    ]

    for user in users:
        db.session.add(User(**user))

    db.session.commit()

    return db
