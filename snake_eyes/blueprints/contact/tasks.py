from uuid import uuid4
from snake_eyes.app import create_celery
from config.settings import EMAIL_SERVICE_HOST
from requests import post
from requests.exceptions import RequestException

celery = create_celery()


@celery.task()
def deliver_contact_email(email, message):
    """
    Send a contact e-mail.

    :param email: E-mail address of the visitor
    :type user_id: str
    :param message: E-mail message
    :type user_id: str
    :return: None
    """
    try:
        url = f"{EMAIL_SERVICE_HOST}/api/email/"
        payload = {
            "sender": email,
            "receiver": celery.conf.get("MAIL_USERNAME"),
            "subject": "[Snake Eyes] Contact",
            "template_id": 1,
            "request_id": uuid4().hex,
            "template_params": {"email": email, "message": message}
        }
        response = post(url, json=payload, headers={"Accept": "application/json"})
    except RequestException as e:
        print(f"[********] UNABLE TO DELIEVER MAIL {e}")
