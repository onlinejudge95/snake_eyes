import pytest

from snake_eyes.app import create_app


@pytest.fixture(scope="session")
def app():
    """
    Setup a test app for snake_eyes.
    Session scopes makes it live for the entire duration of the test

    :return: snake_eyes app
    """
    params = {
        "DEBUG": False,
        "TESTING": True
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
