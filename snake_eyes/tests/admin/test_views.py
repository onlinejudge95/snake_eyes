from flask import url_for

from lib.src.util_tests import ViewTestMixin
from lib.src.util_tests import assert_status_with_message
from snake_eyes.blueprints.user.models import User


class TestDashboardView(ViewTestMixin):
    def test_dashboard_page(self):
        """
        Test dashboard page renders correctly
        """
        self.login()

        response = self.client.get(url_for("admin.dashboard"))

        assert bytes("User".encode("utf-8")) in response.data


class TestUsersView(ViewTestMixin):
    def test_index_page(self):
        """
        Test index page renders correctly
        """
        self.login()

        response = self.client.get(url_for("admin.users"))

        assert response.status_code == 200

    def test_edit_user_page(self):
        """
        Test edit page renders correctly
        """
        self.login()

        response = self.client.get(url_for("admin.users_edit", id=1))

        assert_status_with_message(
            200,
            response,
            "admin@localhost"
        )

    def test_edit_user(self):
        """
        Test editing a resource works correctly
        """
        self.login()

        user = {
            "role": "admin",
            "username": "admin",
            "active": True
        }
        response = self.client.post(
            url_for("admin.users_edit", id=1),
            data=user,
            follow_redirects=True
        )

        assert_status_with_message(
            200,
            response,
            "User has been saved successfully"
        )

    def test_bulk_delete_invalid(self):
        """
        Test bulk delete does nothing to last admin
        """
        self.login()

        old_count = User.query.count()
        bulk_ids = {
            "scope": "all_selected_items",
            "bulk_ids": [1]
        }
        response = self.client.post(
            url_for("admin.users_bulk_delete"),
            data=bulk_ids,
            follow_redirects=True
        )

        assert_status_with_message(
            200,
            response,
            "0 users(s) were scheduled for deletion"
        )

        new_count = User.query.count()
        assert old_count == new_count
