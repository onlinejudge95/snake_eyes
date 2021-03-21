from lib.src.mail import send_templated_message
from snake_eyes.app import create_celery


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
    context = {"email": email, "message": message}

    send_templated_message(subject="[Snake Eyes] Contact", sender=email, recipients=[celery.conf.get("MAIL_USERNAME")], reply_to=email, template="contact/mail/index", context=context)
