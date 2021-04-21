from wtforms.validators import ValidationError

from snake_eyes.blueprints.user.models import User


def ensure_identity_exists(form, field):
    """
    Ensures that an identity exists.

    :param form: wtForms instance
    :param field: Field being passed in
    """
    if not User.find_by_identity(field.data):
        raise ValidationError("Unable to locate the user")


def ensure_existing_password_matches(form, field):
    """
    Ensures that the current password matches the existing password

    :param form: wtForms instance
    :param field: Field being passed in
    """
    if not User.query.get(form._obj.id).authenticated(password=field.data):
        raise ValidationError("Does not matches")
