from datetime import datetime
from pytz import utc

from config import settings
from lib.src.util_sqlalchemy import ResourceMixin
from snake_eyes.blueprints.bet.models.coin import add_subscription_coins
from snake_eyes.blueprints.billing.gateways.stripecom import Card as PaymentCard  # noqa: E501
from snake_eyes.blueprints.billing.gateways.stripecom import Customer as PaymentCustomer  # noqa: E501
from snake_eyes.blueprints.billing.gateways.stripecom import Subscription as PaymentSubscription  # noqa: E501
from snake_eyes.blueprints.billing.models.coupon import Coupon
from snake_eyes.blueprints.billing.models.credit_card import CreditCard
from snake_eyes.extensions import db


class Subscription(ResourceMixin, db.Model):
    __tablename__ = "subscriptions"

    id = db.Column(db.Integer, primary_key=True)

    # Relationships
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
        index=True, nullable=False
    )

    # Subscription details.
    plan = db.Column(db.String(128))
    coupon = db.Column(db.String(128))

    def __init__(self, **kwargs):
        super(Subscription, self).__init__(**kwargs)

    @classmethod
    def get_plan_by_id(cls, plan):
        """
        Pick the plan based on the plan identifier.

        :param plan: Plan identifier
        :type plan: str
        :return: dict or None
        """
        for key, value in settings.STRIPE_PLANS.items():
            if value.get("id") == plan:
                return settings.STRIPE_PLANS[key]

    @classmethod
    def get_new_plan(cls, keys):
        """
        Pick the plan based on the plan identifier.

        :param keys: Keys to look through
        :type keys: list
        :return: str or None
        """
        for key in keys:
            split_key = key.split("submit_")

            if isinstance(split_key, list) and len(split_key) == 2:
                if Subscription.get_plan_by_id(split_key[1]):
                    return split_key[1]

    def create(self, user=None, name=None, plan=None, coupon=None, token=None):
        """
        Create a recurring subscription.

        :param user: User to apply the subscription to
        :type user: User instance
        :param name: User's billing name
        :type name: str
        :param plan: Plan identifier
        :type plan: str
        :param coupon: Coupon code to apply
        :type coupon: str
        :param token: Token returned by JavaScript
        :type token: str
        :return: bool
        """
        if token is None:
            return False

        if coupon:
            self.coupon = coupon.upper()

        customer = PaymentCustomer.create(
            token=token, email=user.email, plan=plan, coupon=self.coupon
        )

        user.payment_id = customer.id
        user.name = name
        user.previous_plan = plan
        user.coins = add_subscription_coins(
            user.coins, Subscription.get_plan_by_id(user.previous_plan),
            Subscription.get_plan_by_id(plan), user.cancelled_subscription_on
        )
        user.cancelled_subscription_on = None

        self.user_id = user.id
        self.plan = plan

        if coupon:
            coupon = Coupon \
                .query \
                .filter(Coupon.code == self.coupon) \
                .first()
            coupon.redeem()

        credit_card = CreditCard(
            user_id=user.id,
            **CreditCard.extract_card_params(customer)
        )

        db.session.add(user)
        db.session.add(credit_card)
        db.session.add(self)

        db.session.commit()

        return True

    def update(self, user=None, coupon=None, plan=None):
        """
        Update an existing subscription.

        :param user: User to apply the subscription to
        :type user: User instance
        :param coupon: Coupon code to apply
        :type coupon: str
        :param plan: Plan identifier
        :type plan: str
        :return: bool
        """
        PaymentSubscription.update(user.payment_id, coupon, plan)

        user.previous_plan = user.subscription.plan
        user.subscription.plan = plan
        user.coins = add_subscription_coins(
            user.coins, Subscription.get_plan_by_id(user.previous_plan),
            Subscription.get_plan_by_id(plan), user.cancelled_subscription_on
        )

        if coupon:
            user.subscription.coupon = coupon
            coupon = Coupon \
                .query \
                .filter(Coupon.code == coupon) \
                .first()

            if coupon:
                coupon.redeem()

        db.session.add(user.subscription)
        db.session.commit()

        return True

    def cancel(self, user=None, discard_credit_card=True):
        """
        Cancel an existing subscription.

        :param user: User to apply the subscription to
        :type user: User instance
        :param discard_credit_card: Delete the user's credit card
        :type discard_credit_card: bool
        :return: bool
        """
        PaymentSubscription.cancel(user.payment_id)

        user.payment_id = None
        user.cancelled_subscription_on = datetime.now(utc)
        user.previous_plan = user.subscription.plan

        db.session.add(user)
        db.session.delete(user.subscription)

        if discard_credit_card:
            db.session.delete(user.credit_card)

        db.session.commit()

        return True

    def update_payment_method(
        self, user=None, credit_card=None, name=None, token=None
    ):
        """
        Update the subscription.

        :param user: User to modify
        :type user: User instance
        :param credit_card: Card to modify
        :type credit_card: Credit Card instance
        :param name: User's billing name
        :type name: str
        :param token: Token returned by JavaScript
        :type token: str
        :return: bool
        """
        if token is None:
            return False

        customer = PaymentCard.update(user.payment_id, token)
        user.name = name

        new_credit_card = CreditCard.extract_card_params(customer)
        credit_card.brand = new_credit_card.get("brand")
        credit_card.last4 = new_credit_card.get("last4")
        credit_card.exp_date = new_credit_card.get("exp_date")
        credit_card.is_expiring = new_credit_card.get("is_expiring")

        db.session.add(user)
        db.session.add(credit_card)

        db.session.commit()

        return True
