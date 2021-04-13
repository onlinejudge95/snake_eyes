from flask import url_for

from lib.src.util_tests import assert_status_with_message


class TestContactView:
    def test_contact_page(self, client):
        """
        Contact page should respond with a success 200.
        """
        contact_page_url = url_for("contact.index")
        response = client.get(contact_page_url)

        assert response.status_code == 200

    def test_contact_form(self, client):
        """
        Contact form should redirect with a message.
        """
        payload = {
            "email": "foo@example.com",
            "message": "Test message"
        }

        contact_page_url = url_for("contact.index")
        response = client.post(
            contact_page_url,
            data=payload,
            follow_redirects=True
        )

        assert_status_with_message(200, response, "Thanks")
