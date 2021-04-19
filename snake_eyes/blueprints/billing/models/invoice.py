from datetime import datetime

from lib.src.util_sqlalchemy import ResourceMixin
from snake_eyes.blueprints.billing.gateways.stripecom import Invoice as PaymentInvoice  # noqa: E501
from snake_eyes.extensions import db


class Invoice(ResourceMixin, db.Model):
    __tablename__ = "invoice"

    id = db.Column(db.Integer, primary_key=True)

    # Relationships
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
        index=True, nullable=False
    )

    # Invoice details
    plan = db.Column(db.String(128), index=True)
    receipt_number = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128))
    period_start_on = db.Column(db.Date)
    period_end_on = db.Column(db.Date)
    currency = db.Column(db.String(8))
    tax = db.Column(db.Integer())
    tax_percent = db.Column(db.Float())
    total = db.Column(db.Integer())

    brand = db.Column(db.String(32))
    last4 = db.Column(db.Integer())
    exp_date = db.Column(db.Date, index=True)

    def __init__(self, **kwargs):
        super(Invoice, self).__init__(**kwargs)

    @classmethod
    def billing_history(cls, user=None):
        """
        Get billing history of a user

        :param user: User whose billing history is required
        :type user: SQLAlchemy instance
        :return: Invoice
        """
        return Invoice \
            .query \
            .filter(Invoice.user_id == user.id) \
            .order_by(Invoice.created_on.desc()) \
            .limit(12)

    @classmethod
    def parse_from_event(cls, payload):
        """
        Parse, save and return the invoice information

        :return: dict
        """
        data = payload["data"]["object"]

        return {
            "payment_id": data["customer"],
            "plan": data["lines"]["data"][0]["plan"]["name"],
            "receipt_number": data["receipt_number"],
            "description": data["description"],
            "period_start_on": datetime.utcfromtimestamp(
                data["lines"]["data"][0]["period"]["start"]
            ).date(),
            "period_end_on": datetime.utcfromtimestamp(
                data["lines"]["data"][0]["period"]["end"]
            ).date(),
            "currency": data["currency"],
            "tax": data["tax"],
            "tax_percent": data["tax_percent"],
            "total": data["total"]
        }

    @classmethod
    def parse_from_api(cls, payload):
        """
        Parse and return the invoice information

        :return: dict
        """
        plan_info = payload["lines"]["data"][0]["plan"]

        return {
            "plan": plan_info["name"],
            "description": plan_info["statement_descriptor"],
            "next_bill_on": datetime.utcfromtimestamp(payload["date"]),
            "amount_due": payload["amount_due"],
            "interval": plan_info["interval"]
        }

    @classmethod
    def prepare_and_save(cls, parsed_event):
        """
        Prepare and save the Invoice.

        :param parsed_events: Event to be saved
        :type parsed_events: dict
        :return: User Instance
        """
        from snake_eyes.blueprints.user.models import User

        user = User \
            .query \
            .filter(User.payment_id == parsed_event.get("payment_id")) \
            .first()

        if user and user.credit_card:
            parsed_event["user_id"] = user.id
            parsed_event["brand"] = user.credit_card.brand
            parsed_event["last4"] = user.credit_card.last4
            parsed_event["exp_date"] = user.credit_card.exp_date

            del parsed_event["payment_id"]

            invoice = Invoice(**parsed_event)
            invoice.save()

        return user

    @classmethod
    def upcoming(cls, customer_id):
        """
        Return the upcoming invoice item.

        :param customer_id: Stripe customer id
        :type customer_id: int
        :return: Stripe invoice object
        """
        # print(Invoice.parse_from_api(PaymentInvoice.upcoming(customer_id)))
        return Invoice.parse_from_api(PaymentInvoice.upcoming(customer_id))
