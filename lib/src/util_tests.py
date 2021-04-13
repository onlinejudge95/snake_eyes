from flask import url_for
from pytest import fixture


class ViewTestMixin:
    """
    Automatically loads a session and a client
    """
    @fixture(autouse=True)
    def set_common_fixtures(self, session, client):
        self.session = session
        self.client = client

    def login(self, identity="admin@localhost", password="password"):
        return login(self.client, identity, password)

    def logout(self):
        return logout(self.client)


def assert_status_with_message(status_code=200, response=None, message=None):
    """
    Check to see if a message is contained within a response.

    :param status_code: Status code that defaults to 200
    :type status_code: int
    :param response: Flask response
    :type response: str
    :param message: String to check for
    :type message: str
    :return: None
    """
    assert response.status_code == status_code
    assert message in str(response.data)


def login(client, identity="", password=""):
    user = dict(identity=identity, password=password)

    return client.post(url_for("user.login"), data=user, follow_redirects=True)


def logout(client):
    return client.get(url_for("user.logout"), follow_redirects=True)
