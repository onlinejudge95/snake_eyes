from collections import OrderedDict

from flask_wtf import Form
from wtforms import BooleanField
from wtforms import DateTimeField
from wtforms import FloatField
from wtforms import IntegerField
from wtforms import StringField
from wtforms import SelectField
from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import NumberRange
from wtforms.validators import Optional
from wtforms.validators import Regexp
from wtforms_components import Unique

from lib.src.util_forms import ModelForm
from lib.src.util_forms import choices_from_dict
from lib.src.util_locale import Currency
from snake_eyes.blueprints.billing.models.coupon import Coupon
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
    coins = IntegerField(
        "Coins",
        [DataRequired(), NumberRange(min=1, max=2147483647)]
    )
    role = SelectField(
        "Privileges",
        [DataRequired()],
        choices=choices_from_dict(User.ROLE, prepend_blank=False)
    )
    active = BooleanField("Yes, allow this user to sign in")


class UserCancelSubscriptionForm(Form):
    pass


class CouponForm(Form):
    percent_off = IntegerField(
        "Percent off (%)", [Optional(), NumberRange(min=1, max=100)]
    )
    amount_off = FloatField(
        "Amount off ($)", [Optional(), NumberRange(min=0.01, max=21474836.47)]
    )
    code = StringField("Code", [DataRequired(), Length(1, 32)])
    currency = SelectField(
        "Currency", [DataRequired()],
        choices=choices_from_dict(Currency.TYPES, prepend_blank=False)
    )
    duration = SelectField(
        "Duration", [DataRequired()],
        choices=choices_from_dict(Coupon.DURATION, prepend_blank=False)
    )
    duration_in_months = IntegerField(
        "Duration in months", [Optional(), NumberRange(min=1, max=12)]
    )
    max_redemptions = IntegerField(
        "Max Redemptions", [Optional(), NumberRange(min=1, max=2147483647)]
    )
    redeem_by = DateTimeField(
        "Redeem by", [Optional()], format="%Y-%m-%d %H:%M:%S"
    )

    def validate(self):
        if not Form.validate(self):
            return False

        result = True
        percent_off = self.percent_off.data
        amount_off = self.amount_off.data

        if percent_off is None and amount_off is None:
            error = "Choose at least one"
            result = False
            self.percent_off.errors.append(error)
            self.amount_off.errors.append(error)
        elif percent_off and amount_off:
            error = "Cannot pick both"
            result = False
            self.percent_off.errors.append(error)
            self.amount_off.errors.append(error)

        return result
