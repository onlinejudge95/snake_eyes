from flask import url_for

from lib.src.util_tests import ViewTestMixin
from lib.src.util_tests import assert_status_with_message
from snake_eyes.blueprints.user.models import User


class TestLoginView(ViewTestMixin):
    def test_login_page(self):
        """
        Test if login page renders correctly
        """
        response = self.client.get(url_for("user.login"))

        assert response.status_code == 200

    def test_login(self):
        """
        Test login flow works correctly
        """
        response = self.login()

        assert response.status_code == 200

    def test_login_activity(self, users):
        """
        Login activity recording works correctly
        """
        user = User.find_by_identity("admin@localhost")
        old_sign_in_count = user.sign_in_count

        response = self.login()
        new_sign_in_count = user.sign_in_count

        assert response.status_code == 200
        assert old_sign_in_count + 1 == new_sign_in_count

    def test_login_disable(self):
        """
        Test diabled user can't login
        """
        response = self.login(identity="disabl@localhost")

        assert_status_with_message(
            200,
            response,
            "The account is disabled"
        )

    def test_login_fail(self):
        """
        Test invalid creds for login
        """
        response = self.login(identity="foo@bar")

        assert_status_with_message(
            200,
            response,
            "Identity or password is incorrect"
        )

    def test_logout(self):
        """
        Test logout works successfully
        """
        self.login()

        response = self.logout()

        assert_status_with_message(200, response, "You have been logged out")


class TestPasswordResetView(ViewTestMixin):
    def test_begin_password_reset_page(self):
        """
        Test begin password reset page renders correctly
        """
        response = self.client.get(url_for("user.begin_password_reset"))

        assert response.status_code == 200

    def test_password_reset_page(self):
        """
        Test password reset renders successfully
        """
        response = self.client.get(url_for("user.password_reset"))
        assert response.status_code == 200

    def test_begin_password_reset_as_logged_in(self):
        """
        Test begin password reset redirects to settings
        """
        self.login()

        response = self.client.get(
            url_for("user.begin_password_reset"),
            follow_redirects=False
        )
        assert response.status_code == 302

    def test_password_reset_as_logged_in(self):
        """
        Test password reset redirects to settings
        """
        self.login()

        response = self.client.get(
            url_for("user.password_reset"),
            follow_redirects=False
        )
        assert response.status_code == 302

    def test_begin_password_reset_fail(self):
        """
        Test being password reset fails due to non existing user
        """
        user = {"identity": "foo@invalid.com"}
        response = self.client.post(
            url_for("user.begin_password_reset"),
            data=user,
            follow_redirects=True
        )

        assert_status_with_message(
            200,
            response,
            "Unable to locate the user"
        )

    def test_begin_password_reset(self):
        """
        Test password reset works correctly
        """
        user = {"identity": "admin@localhost"}
        response = self.client.post(
            url_for("user.begin_password_reset"),
            data=user,
            follow_redirects=True
        )

        assert_status_with_message(
            200,
            response,
            f"An email with instructions have been sent to {user['identity']}"
        )

    def test_password_reset(self, users, token):
        """
        Test password reset works correctly
        """
        reset = {"password": "newpassword", "reset_token": token}
        response = self.client.post(
            url_for("user.password_reset"),
            data=reset,
            follow_redirects=True
        )

        assert_status_with_message(
            200,
            response,
            "Your password has been reset"
        )

    def test_password_reset_empty_token(self):
        """
        Test password reset fails due to inactive token
        """
        reset = {"password": "newpassword"}
        response = self.client.post(
            url_for("user.password_reset"),
            data=reset,
            follow_redirects=True
        )

        assert_status_with_message(
            200,
            response,
            "Your reset token has expired or tampered with"
        )

    def test_password_reset_invalid_token(self):
        """
        Test password reset fails due to invalid token
        """
        reset = {"password": "newpassword", "token": "1234567890"}
        response = self.client.post(
            url_for("user.password_reset"),
            data=reset,
            follow_redirects=True
        )

        assert_status_with_message(
            200,
            response,
            "Your reset token has expired or tampered with"
        )


class TestSignupView(ViewTestMixin):
    def test_signup_page(self):
        """
        Tests signup page renders correctly
        """
        response = self.client.get(url_for("user.signup"))

        assert response.status_code == 200

    # def test_welcome_page(self):
    #     """
    #     Test welcome page renders correctly
    #     """
    #     self.login()
        
    #     response = self.client.get(url_for("user.welcome"))

    #     assert response.status_code == 200

    def test_begin_signup_fail_logged_in(self, users):
        """
        Test signup fails when already logged in
        """
        self.login()

        response = self.client.get(
            url_for("user.signup"),
            follow_redirects=False
        )

        assert response.status_code == 302

    def test_begin_signup_fail_already_exists(self):
        """
        Test begin signup fails when the user already exists.
        """
        user = {"email": "admin@localhost", "password": "password"}
        response = self.client.post(
            url_for("user.signup"),
            data=user,
            follow_redirects=True
        )

        assert_status_with_message(
            200,
            response,
            "Already exists"
        )

    def test_signup(self):
        """
        Test signup flow works correctly
        """
        old_user_count = User.query.count()

        user = {"email": "user@localhost", "password": "password"}
        response = self.client.post(
            url_for("user.signup"),
            data=user,
            follow_redirects=True
        )

        assert_status_with_message(
            200,
            response,
            "Awesome, thanks for signing up"
        )

        new_user_count = User.query.count()

        assert old_user_count + 1 == new_user_count
        assert User.find_by_identity("user@localhost").password != user["password"]

    def test_welcome(self):
        """
        Test welcome flow works correctly
        """
        self.login()

        user = {"username": "hello"}
        response = self.client.post(
            url_for("user.welcome"),
            data=user,
            follow_redirects=True
        )

        assert_status_with_message(
            200,
            response,
            "Signup is complete"
        )

    def test_welcome_with_existing_username(self):
        """
        Test welcome flow fails when username already exists
        """
        self.login()

        user = User.find_by_identity("admin@localhost")
        user.username = "user"
        user.save()

        user = {"username": "newuser"}
        response = self.client.post(
            url_for("user.welcome"),
            data=user,
            follow_redirects=True
        )

        assert_status_with_message(
            200,
            response,
            "You have already picked a username"
        )


class TestSettingsView(ViewTestMixin):
    def test_settings_page(self):
        """
        Test settings page renders correctly
        """
        self.login()

        response = self.client.get(url_for("user.settings"))

        assert response.status_code == 200


class TestUpdateCredentialsView(ViewTestMixin):
    def test_update_credentials_page(self):
        """
        Test update credentials page renders corectly
        """
        self.login()

        response = self.client.get(url_for("user.update_credentials"))

        assert response.status_code == 200

    def test_begin_update_credentials_invalid_password(self):
        """
        Test update credentials fails due to incorrect current password
        """
        self.login()

        user = {"current_password": "wrongpassword", "email": "admin@localhost"}
        response = self.client.post(
            url_for("user.update_credentials"),
            data=user,
            follow_redirects=True
        )

        assert_status_with_message(
            200,
            response,
            "Does not match"
        )

    # def test_begin_update_credentials_deactivated_account(self):
    #     """
    #     Test update credentials fails due problems with email of the account
    #     """
    #     self.login()

    #     user = {"current_password": "password", "email": "disabl@localhost"}
    #     response = self.client.post(
    #         url_for("user.update_credentials"),
    #         data=user,
    #         follow_redirects=True
    #     )

    #     assert_status_with_message(
    #         200,
    #         response,
    #         "Already exists"
    #     )

    def test_begin_update_credentials_email_change(self):
        """
        Test updating only the email address works correctly
        """
        self.login()

        user = {"current_password": "password", "email": "admin2@localhost"}
        response = self.client.post(
            url_for("user.update_credentials"),
            data=user,
            follow_redirects=True
        )

        assert_status_with_message(
            200,
            response,
            "Your sign in settings are updated"
        )

    def test_begin_update_credentials_password_change(self):
        """
        Test updating only the password works correctly
        """
        self.login()

        user = {"current_password": "password", "email": "admin@localhost", "password": "newpassword"}
        response = self.client.post(
            url_for("user.update_credentials"),
            data=user,
            follow_redirects=True
        )

        assert response.status_code == 200

        self.logout()
        self.login()

        assert response.status_code == 200

    def test_begin_update_credentials_email_password(self):
        """
        Test updating both the email and the password works correctly
        """
        self.login()

        user = {"current_password": "password", "email": "admin2@localhost", "password": "newpassword"}
        response = self.client.post(
            url_for("user.update_credentials"),
            data=user,
            follow_redirects=True
        )

        assert response.status_code == 200
