from snake_eyes.blueprints.contact.tasks import deliver_contact_email
from snake_eyes.extensions import mail


class TestContactTask:
    def test_deliever_support_email(self):
        """
        Deliver a contact email.
        """
        payload = {"email": "foo@example.com", "message": "Test message"}

        with mail.record_messages() as outbox:
            deliver_contact_email(email=payload["email"], message=payload["message"])

            assert len(outbox) == 1
            assert payload["email"] in outbox[0].body
