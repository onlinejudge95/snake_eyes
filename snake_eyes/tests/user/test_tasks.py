from snake_eyes.blueprints.user.models import User
from snake_eyes.blueprints.user.tasks import deliever_password_reset_mail
from snake_eyes.extensions import mail


class TestTasks:
    def test_deliever_password_reset_email(self, token):
        """Test if a password reset mail is delievered properly"""

        with mail.record_messages() as outbox:
            user = User.find_by_identity("admin@localhost")
            deliever_password_reset_mail(user.id, token)

            assert len(outbox) == 1
            assert token in outbox[0].body
