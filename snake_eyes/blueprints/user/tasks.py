from uuid import uuid4

from snake_eyes.app import create_celery
from snake_eyes.blueprints.user.models import User
from config.settings import EMAIL_SERVICE_HOST
from config.settings import MAIL_DEFAULT_SENDER
from requests import post
from requests.exceptions import RequestException


celery = create_celery()


@celery.task()
def deliever_password_reset_mail(user_id, reset_password_url):
    """
    Send a password reset email to the suer

    :param user_id: ID of the user
    :type user_id: int
    :param reset_password_url: Reset Password URL
    :type reset_password_url: str
    """
    user = User.query.get(user_id)

    if user is not None:
        try:
            url = f"{EMAIL_SERVICE_HOST}/api/email/"
            payload = {
                "sender": MAIL_DEFAULT_SENDER,
                "receiver": user.email,
                "subject": "Password reset from snake eyes",
                "template_id": 2,
                "request_id": uuid4().hex,
                "template_params": {"username": user.username, "reset_password_url": reset_password_url}
            }
            response = post(url, json=payload, headers={"Accept": "application/json"})
        except RequestException as e:
            print(f"[********] UNABLE TO DELIEVER MAIL {e}")
