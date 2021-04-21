from collections import OrderedDict
from datetime import datetime
from random import choice
from string import ascii_uppercase
from string import digits

from pytz import UTC
from pytz import utc
from sqlalchemy import and_
from sqlalchemy import or_
from sqlalchemy.ext.hybrid import hybrid_property

from lib.src.util_money import cents_to_dollars
from lib.src.util_money import dollars_to_cents
from lib.src.util_sqlalchemy import AwareDateTime
from lib.src.util_sqlalchemy import ResourceMixin
from snake_eyes.blueprints.billing.gateways.stripecom import Coupon as PaymentCoupon  # noqa: E501
from snake_eyes.extensions import db


class Coupon(ResourceMixin, db.Model):
    DURATION = OrderedDict([
        ("forever", "Forever"),
        ("once", "Once"),
        ("repeating", "Repeating")
    ])

    __tablename__ = "coupons"

    id = db.Column(db.Integer, primary_key=True)

    code = db.Column(db.String(128), index=True, unique=True)
    duration = db.Column(
        db.Enum(*DURATION, name="duration_types"),
        index=True,
        nullable=False,
        server_default="forever"
    )

    amount_off = db.Column(db.Integer())
    percent_off = db.Column(db.Integer())
    currency = db.Column(db.String(8))
    duration_in_months = db.Column(db.Integer())
    max_redemptions = db.Column(db.Integer(), index=True)
    redeem_by = db.Column(AwareDateTime(), index=True)
    times_redeemed = db.Column(
        db.Integer(),
        index=True,
        nullable=False,
        default=0
    )
    valid = db.Column(db.Boolean(), nullable=False, server_default="1")

    def __init__(self, **kwargs):
        self.code = self.code.upper() \
            if self.code else Coupon.random_coupon_code()
        super(Coupon, self).__init__(**kwargs)

    @hybrid_property
    def redeemable(self):
        """
        Return coupons that are redeemable

        :return: SQLAlchemy query object
        """
        is_redeemable = or_(
            self.redeem_by.is_(None),
            self.redeem_by >= datetime.now(utc)
        )

        return and_(self.valid, is_redeemable)

    @classmethod
    def random_coupon_code(cls):
        """
        Create a human readable random coupon code
        :return: str
        """
        charset = digits + ascii_uppercase
        charset = charset.replace("B", "").replace("I", "")
        charset = charset.replace("O", "").replace("S", "")
        charset = charset.replace("0", "").replace("1", "")

        samples = "".join(choice(charset) for _ in range(14))

        return f"{samples[0:4]}-{samples[5:9]}-{samples[10:14]}"

    @classmethod
    def search(cls, query):
        """
        Search a resource by 1 or more fields.

        :param query: Search query
        :type query: str
        :return: SQLAlchemy filter object
        """
        if query:
            search_query = f"%{query}%"
            return or_(Coupon.code.ilike(search_query))

        return ""

    @classmethod
    def expire_old_coupons(cls, compare_datetime=datetime.now(utc)):
        """
        Invalidate expired coupons

        :param compare_datetime: Time to compare at
        :type compare_datetime: date
        :return: SQLAlchemy commit object
        """
        Coupon \
            .query \
            .filter(Coupon.redeem_by <= compare_datetime) \
            .update({Coupon.valid: not Coupon.valid})

        return db.session.commit()

    @classmethod
    def create(cls, params):
        """
        Create a coupon and return the status

        :param params: Parameters for coupon creation
        :type params: dict
        :return: bool
        """
        payment_params = params
        payment_params["code"] = payment_params["code"].upper()

        if payment_params.get("amount_off"):
            payment_params["amount_off"] = dollars_to_cents(
                payment_params["amount_off"]
            )

        PaymentCoupon.create(**payment_params)

        if "id" in payment_params:
            payment_params["code"] = payment_params["id"]
            del payment_params["id"]

        if "redeem_by" in payment_params:
            if payment_params.get("redeem_by") is not None:
                payment_params["redeem_by"] = payment_params\
                    .get("redeem_by") \
                    .replace(tzinfo=UTC)

        coupon = Coupon(**payment_params)

        db.session.add(coupon)
        db.session.commit()

        return True

    @classmethod
    def bulk_delete(cls, ids):
        """
        Overriding the general bulk_delete method as we
        also need to delete them one at a time while deleting
        the from Stripe

        :param ids: List fo ids of coupons to be deleted
        :type ids: list
        :return: int
        """
        count = 0

        for _id in ids:
            coupon = Coupon.query.get(_id)

            if coupon is not None:
                stripe_response = PaymentCoupon.delete(coupon.code)

                if stripe_response.get("deleted"):
                    coupon.delete()
                    count += 1

        return count

    @classmethod
    def find_by_code(cls, code):
        """
        Find a coupon by its code.

        :param code: Coupon code to find
        :type code: str
        :return: Coupon instance
        """
        return Coupon \
            .query \
            .filter(Coupon.redeemable, Coupon.code == code.upper()) \
            .first()

    def redeem(self):
        """
        Update the redeem stats for this coupon.

        :return: Result of saving the record
        """
        self.times_redeemed += 1

        if self.max_redemptions:
            if self.times_redeemed >= self.max_redemptions:
                self.valid = False

        return db.session.commit()

    def to_json(self):
        """
        Return JSON fields to represent a coupon.

        :return: dict
        """
        params = {
            "duration": self.duration,
            "duration_in_months": self.duration_in_months
        }

        if self.amount_off:
            params["amount_off"] = cents_to_dollars(self.amount_off)

        if self.percent_off:
            params["percent_off"] = self.percent_off

        return params

    def apply_discount_to(self, amount):
        """
        Apply the discount to an amount.

        :param amount: Amount in cents
        :type amount: int
        :return: int
        """
        if self.amount_off:
            amount -= self.amount_off
        elif self.percent_off:
            amount *= (1 - (self.percent_off * 0.01))

        return int(amount)
