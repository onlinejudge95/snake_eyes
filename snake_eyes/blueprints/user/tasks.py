from lib.src.util_mail import send_templated_message
from snake_eyes.app import create_celery
from snake_eyes.blueprints.user.models import User


celery = create_celery()


@celery.task()
def deliever_password_reset_mail(user_id, reset_token):
    """
    Send a password reset email to the suer

    :param user_id: ID of the user
    :type user_id: int
    :param reset_token: Reset token
    :type reset_token: str
    """
    user = User.query.get(user_id)

    if user is not None:
        context = {"user": user, "reset_token": reset_token}

        send_templated_message(
            subject="Password reset from snake eyes",
            recipients=[user.email],
            template="user/mail/password_reset",
            context=context
        )
