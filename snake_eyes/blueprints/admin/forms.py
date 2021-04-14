from collections import OrderedDict

from flask_wtf import Form
from wtforms import BooleanField
from wtforms import StringField
from wtforms import SelectField
from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import Optional
from wtforms.validators import Regexp
from wtforms_components import Unique

from lib.src.util_forms import ModelForm
from lib.src.util_forms import choices_from_dict
from snake_eyes.blueprints.user.models import User
from snake_eyes.blueprints.user.models import db


class BulkDeleteForm(Form):
    SCOPE = OrderedDict([
        ("all_selected_items", "All selected items"),
        ("all_search_results", "All search items")
    ])

    scope = SelectField(
        "Privileges",
        [DataRequired()],
        choices=choices_from_dict(SCOPE, prepend_blank=False)
    )


class SearchForm(Form):
    q = StringField("Search terms", [DataRequired(), Length(1, 256)])


class UserForm(ModelForm):
    error_message = "Letters, numbers and underscore is allowed."

    username = StringField(
        validators=[
            Unique(User.username, get_session=lambda: db.session),
            Optional(),
            Length(1, 16),
            Regexp(r"^\w+$", message=error_message)
        ]
    )
    role = SelectField(
        "Privileges",
        [DataRequired()],
        choices=choices_from_dict(User.ROLE, prepend_blank=False)
    )
    active = BooleanField("Yes, allow this user to sign in")
