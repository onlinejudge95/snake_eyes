from flask_wtf import Form
from wtforms import HiddenField
from wtforms import PasswordField
from wtforms import SelectField
from wtforms import StringField
from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import Optional
from wtforms.validators import Regexp
from wtforms_components import Email
from wtforms_components import EmailField
from wtforms_components import Unique

from config.settings import LANGUAGES
from lib.src.util_forms import ModelForm
from lib.src.util_forms import choices_from_dict
from snake_eyes.blueprints.user.models import User
from snake_eyes.blueprints.user.models import db
from snake_eyes.blueprints.user.validations import (
    ensure_existing_password_matches,
)
from snake_eyes.blueprints.user.validations import ensure_identity_exists


class LoginForm(Form):
    next = HiddenField()
    identity = StringField("Username or Email", [DataRequired(), Length(3, 254)])
    password = PasswordField("Password", [DataRequired(), Length(8, 128)])


class BeginPasswordResetForm(Form):
    identity = StringField(
        "Username or Email", [DataRequired(), Length(3, 254), ensure_identity_exists]
    )


class PasswordResetForm(Form):
    reset_token = HiddenField()
    password = PasswordField("Password", [DataRequired(), Length(8, 128)])


class SignupForm(ModelForm):
    email = EmailField(
        validators=[
            DataRequired(),
            Email(),
            Unique(User.email, get_session=lambda: db.session),
        ]
    )
    password = PasswordField("Password", [DataRequired(), Length(8, 128)])


class WelcomeForm(ModelForm):
    error_message = "Letters, numbers and underscore is allowed."

    username = StringField(
        validators=[
            DataRequired(),
            Length(1, 16),
            Unique(User.username, get_session=lambda: db.session),
            Regexp(r"^\w+$", message=error_message),
        ]
    )


class UpdateCredentials(ModelForm):
    current_password = PasswordField(
        "Current password",
        [DataRequired(), Length(8, 128), ensure_existing_password_matches],
    )
    email = EmailField(
        validators=[Email(), Unique(User.email, get_session=lambda: db.session)]
    )
    password = PasswordField("Password", [Optional(), Length(8, 128)])


class UpdateLocaleForm(Form):
    locale = SelectField(
        "Language Preference",
        [DataRequired()],
        choices=choices_from_dict(LANGUAGES, prepend_blank=False),
    )
