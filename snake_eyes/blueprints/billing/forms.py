from flask_wtf import Form
from wtforms import HiddenField
from wtforms import StringField
from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import Optional


class CreditCardForm(Form):
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
