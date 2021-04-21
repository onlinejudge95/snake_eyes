from flask_wtf import Form
from wtforms import HiddenField
from wtforms import SelectField
from wtforms import StringField
from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import Optional

from config.settings import COIN_BUNDLES


def choices_from_coin_bundles():
    """
    Convert the COIN_BUNDLE settings into select box items.

    :return: list
    """
    return [
        (str(bundle.get("coins")), bundle.get("label"))
        for bundle in COIN_BUNDLES
    ]


class SubscriptionForm(Form):
    stripe_key = HiddenField(
        "Stripe Publishable Key", [DataRequired(), Length(1, 254)]
    )
    plan = HiddenField("Plan", [DataRequired(), Length(1, 254)])
    coupon_code = StringField(
        "Do you have a coupon code?", [Optional(), Length(1, 128)]
    )
    name = StringField(
        "Name on card", [DataRequired(), Length(1, 254)]
    )


class UpdateSubscriptionForm(Form):
    coupon_code = StringField(
        "Do you have a coupon code?", [Optional(), Length(1, 128)]
    )


class CancelSubscriptionForm(Form):
    pass


class PaymentForm(Form):
    stripe_key = HiddenField(
        "Stripe Publishable Key", [DataRequired(), Length(1, 254)]
    )
    coin_bundles = SelectField(
        "How many coins do you want?", [DataRequired()],
        choices=choices_from_coin_bundles()
    )
    coupon_code = StringField(
        "Do you have a coupon code?", [Optional(), Length(1, 128)]
    )
    name = StringField(
        "Name on card", [DataRequired(), Length(1, 254)]
    )
