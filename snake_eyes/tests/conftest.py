from datetime import date
from datetime import datetime

from mock import Mock
from pytest import fixture
from pytz import utc

from config import settings
from lib.src.util_datetime import timedelta_month
from snake_eyes.app import create_app
from snake_eyes.blueprints.billing.gateways.stripecom import (
    Card as PaymentCard,
)
from snake_eyes.blueprints.billing.gateways.stripecom import (
    Coupon as PaymentCoupon,
)
from snake_eyes.blueprints.billing.gateways.stripecom import (
    Event as PaymentEvent,
)
from snake_eyes.blueprints.billing.gateways.stripecom import (
    Invoice as PaymentInvoice,
)
from snake_eyes.blueprints.billing.gateways.stripecom import (
    Subscription as PaymentSubscription,
)
from snake_eyes.blueprints.billing.models.coupon import Coupon
from snake_eyes.blueprints.billing.models.credit_card import CreditCard
from snake_eyes.blueprints.billing.models.subscription import Subscription
from snake_eyes.blueprints.user.models import User
from snake_eyes.extensions import db as _db


@fixture(scope="session")
def app():
    """
    Setup a test app for snake_eyes.
    Session scopes makes it live for the entire duration of the test.

    :return: snake_eyes app
    """
    params = {
        "DEBUG": False,
        "WTF_CSRF_ENABLED": False,
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"{settings.SQLALCHEMY_DATABASE_URI}_test"
    }
    test_app = create_app(settings_override=params)

    with test_app.app_context():
        yield test_app


@fixture(scope="function")
def client(app):
    """
    Setup a test client from the snake_eyes app.
    This is created for every test function run to provide isolation.

    :param app: Pytest app fixture
    :return: snake_eyes app test client
    """
    yield app.test_client()


@fixture(scope="session")
def db(app):
    """
    Setup a db for testing.
    Session scopes makes it live for the entire duration of the test.

    :param app: Pytest app fixture
    :return: SQLAlchemy database session
    """
    _db.drop_all()
    _db.create_all()

    params = {
        "role": "admin",
        "email": "admin@localhost",
        "password": "password"
    }

    admin = User(**params)

    _db.session.add(admin)
    _db.session.commit()

    return _db


@fixture(scope="function")
def session(db):
    """
    Speeds up testing using rollbacks and nested session.
    Requires the DB to support SQL savepoints.
    This is created for every test function run to provide isolation.

    :param db: Pytest db fixture
    """
    db.session.begin_nested()

    yield db.session

    db.session.rollback()


@fixture(scope="session")
def token(db):
    """
    Serialize a JWS token
    Session scopes makes it live for the entire duration of the test.

    :param db: Pytest db fixture
    :return: JWS Token
    """
    return User.find_by_identity("admin@localhost").serialize_token()


@fixture(scope="function")
def users(db):
    """
    Create user fixtures.
    This is created for every test function run to provide isolation.

    :param db: Pytest db fixture
    :return: SQLAlchemy database session
    """

    db.session.query(User).delete()

    users = [
        {"role": "admin", "email": "admin@localhost", "password": "password"},
        {"active": False, "email": "disabl@localhost", "password": "password"}
    ]

    for user in users:
        db.session.add(User(**user))

    db.session.commit()

    return db


@fixture(scope="function")
def credit_cards(db):
    """
    Create fixture for credit cards
    :param db: Pytest fixture
    :return: SQLAlchemy database instance
    """
    db.session.query(CreditCard).delete()

    may_1_2021 = date(2021, 5, 1)
    june_1_2021 = utc.localize(datetime(2021, 6, 14, 0, 0, 0))

    credit_cards = [
        {
            "user_id": 1, "brand": "Visa", "last4": 4242,
            "exp_date": june_1_2021
        },
        {
            "user_id": 2, "brand": "Visa", "last4": 4242,
            "exp_date": timedelta_month(12, may_1_2021)
        },
    ]

    for credit_card in credit_cards:
        db.session.add(CreditCard(**credit_card))

    db.session.commit()
    return db


@fixture(scope="function")
def coupons(db):
    """
    Create coupon fixtures.

    :param db: Pytest fixture
    :return: SQLAlchemy database session
    """
    db.session.query(Coupon).delete()

    may_1_2021 = utc.localize(datetime(2021, 5, 1, 0, 0, 0))
    june_1_2021 = utc.localize(datetime(2021, 6, 1, 0, 0, 0))

    coupons = [
        {"amount_off": 1, "redeem_by": may_1_2021},
        {"amount_off": 1, "redeem_by": june_1_2021},
        {"amount_off": 1},
    ]

    for coupon in coupons:
        db.session.add(Coupon(**coupon))

    db.session.commit()

    return db


@fixture(scope="function")
def subscriptions(db):
    """
    Create subscription fixtures.

    :param db: Pytest fixture
    :return: SQLAlchemy database session
    """
    subscriber = User.find_by_identity("subscriber@localhost")

    if subscriber:
        subscriber.delete()

    db.session.query(Subscription).delete()

    params = {
        "role": "admin",
        "email": "subscriber@localhost",
        "name": "test_user",
        "password": "password",
        "payment_id": "customer_000"
    }

    subscriber = User(**params)

    db.session.add(subscriber)
    db.session.commit()

    params = {
        "user_id": subscriber.id,
        "plan": "gold"
    }

    subscription = Subscription(**params)
    db.session.add(subscription)

    params = {
        "user_id": subscriber.id,
        "brand": "Visa",
        "last4": "4242",
        "exp_date": date(2021, 6, 1)
    }
    credit_card = CreditCard(**params)
    db.session.add(credit_card)

    db.session.commit()

    return db


@fixture(scope="session")
def mock_stripe():
    """
    Mock all of the Stripe API calls.
    """
    upcoming_invoice_api = {
        "date": 1433018770,
        "id": "in_000",
        "period_start": 1433018770,
        "period_end": 1433018770,
        "lines": {
            "data": [
                {
                    "id": "sub_000",
                    "object": "line_item",
                    "type": "subscription",
                    "livemode": True,
                    "amount": 0,
                    "currency": "usd",
                    "proration": False,
                    "period": {
                        "start": 1433161742,
                        "end": 1434371342
                    },
                    "subscription": None,
                    "quantity": 1,
                    "plan": {
                        "interval": "month",
                        "name": "Gold",
                        "created": 1424879591,
                        "amount": 500,
                        "currency": "usd",
                        "id": "gold",
                        "object": "plan",
                        "livemode": False,
                        "interval_count": 1,
                        "trial_period_days": 14,
                        "metadata": {
                        },
                        "statement_descriptor": "GOLD MONTHLY"
                    },
                    "description": None,
                    "discountable": True,
                    "metadata": {
                    }
                }
            ],
            "total_count": 1,
            "object": "list",
            "url": "/v1/invoices/in_000/lines"
        },
        "subtotal": 0,
        "total": 0,
        "customer": "cus_000",
        "object": "invoice",
        "attempted": True,
        "closed": True,
        "forgiven": False,
        "paid": True,
        "livemode": False,
        "attempt_count": 0,
        "amount_due": 500,
        "currency": "usd",
        "starting_balance": 0,
        "ending_balance": 0,
        "next_payment_attempt": None,
        "webhooks_delivered_at": None,
        "charge": None,
        "discount": None,
        "application_fee": None,
        "subscription": "sub_000",
        "tax_percent": None,
        "tax": None,
        "metadata": {
        },
        "statement_descriptor": None,
        "description": None,
        "receipt_number": None
    }
    PaymentCoupon.create = Mock(return_value={})
    PaymentCoupon.delete = Mock(return_value={})
    PaymentEvent.retrieve = Mock(return_value={})
    PaymentCard.update = Mock(return_value={})
    PaymentSubscription.create = Mock(return_value={})
    PaymentSubscription.update = Mock(return_value={})
    PaymentSubscription.cancel = Mock(return_value={})
    PaymentInvoice.upcoming = Mock(return_value=upcoming_invoice_api)
