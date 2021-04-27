from stripe import Charge as StripeCharge
from stripe import Coupon as StripeCoupon
from stripe import Customer as StripeCustomer
from stripe import Event as StripeEvent
from stripe import Invoice as StripeInvoice
from stripe import Plan as StripePlan
from stripe.error import StripeError


class Coupon:
    @classmethod
    def create(
        cls,
        code=None,
        duration=None,
        amount_off=None,
        percent_off=None,
        currency=None,
        duration_in_months=None,
        max_redemptions=None,
        redeem_by=None,
    ):
        """
        Create a new coupon

        API Documentation:
            https://stripe.com/docs/api#create_coupon

        :param code: Coupon code
        :param duration: How long the coupon will be in effect
        :type duration: str
        :param amount_off: Discount in a fixed amount
        :type amount_off: int
        :param percent_off: Discount based on percent off
        :type percent_off: int
        :param currency: 3 digit currency abbreviation
        :type currency: str
        :param duration_in_months: Number of months in effect
        :type duration_in_months: int
        :param max_redemptions: Max number of times it can be redeemed
        :type max_redemptions: int
        :param redeem_by: Redeemable by this date
        :type redeem_by: date
        :return: Stripe coupon
        """
        return StripeCoupon.create(
            id=code,
            duration=duration,
            amount_off=amount_off,
            percent_off=percent_off,
            currency=currency,
            duration_in_months=duration_in_months,
            max_redemptions=max_redemptions,
            redeem_by=redeem_by,
        )

    @classmethod
    def delete(cls, _id=None):
        """
        Delete an existing coupon

        API Documentation:
          https://stripe.com/docs/api#delete_coupon

        :param id: Coupon code
        :return: Stripe coupon
        """
        coupon = StripeCoupon.retrieve(_id)
        return coupon.delete()


class Invoice:
    @classmethod
    def upcoming(cls, customer_id):
        """
        Retrieve an upcoming invoice item for a user.

        API Documentation:
          https://stripe.com/docs/api#retrieve_customer_invoice

        :param customer_id: Stripe customer id
        :type customer_id: int
        :return: Stripe invoice
        """
        return StripeInvoice.upcoming(customer=customer_id)


class Subscription:
    @classmethod
    def update(cls, customer_id=None, coupon=None, plan=None):
        """
        Update an existing subscription.

        API Documentation:
          https://stripe.com/docs/api/python#update_subscription

        :param customer_id: Customer id
        :type customer_id: str
        :param coupon: Coupon code
        :type coupon: str
        :param plan: Plan identifier
        :type plan: str
        :return: Stripe subscription
        """
        customer = StripeCustomer.retrieve(customer_id)

        subscription_id = customer.subscriptions.data[0].id
        subscription = customer.subscriptions.retrieve(subscription_id)

        subscription.plan = plan

        if coupon:
            subscription.coupon = coupon

        return subscription.save()

    @classmethod
    def cancel(cls, customer_id=None):
        """
        Cancel an existing subscription.

        API Documentation:
          https://stripe.com/docs/api#cancel_subscription

        :param customer_id: Stripe customer id
        :type customer_id: int
        :return: Stripe subscription object
        """
        customer = StripeCustomer.retrieve(customer_id)
        subscription_id = customer.subscriptions.data[0].id

        return customer.subscriptions.retrieve(subscription_id).delete()


class Card:
    @classmethod
    def update(cls, customer_id, stripe_token=None):
        """
        Update an existing card through a customer.

        API Documentation:
          https://stripe.com/docs/api/python#update_card

        :param customer_id: Stripe customer id
        :type customer_id: int
        :param stripe_token: Stripe token
        :type stripe_token: str
        :return: Stripe customer
        """
        customer = StripeCustomer.retrieve(customer_id)
        customer.source = stripe_token

        return customer.save()


class Plan:
    @classmethod
    def retrieve(cls, plan):
        """
        Retrieve an existing plan.

        API Documentation:
          https://stripe.com/docs/api#retrieve_plan

        :param plan: Plan identifier
        :type plan: str
        :return: Stripe plan
        """
        try:

            return StripePlan.retrieve(plan)
        except StripeError as e:
            print(e)

    @classmethod
    def list(cls):
        """
        List all plans.

        API Documentation:
          https://stripe.com/docs/api#list_plans

        :return: Stripe plans
        """
        try:
            return StripePlan.all()
        except StripeError as e:
            print(e)

    @classmethod
    def create(
        cls,
        _id=None,
        name=None,
        amount=None,
        currency=None,
        interval=None,
        interval_count=None,
        trial_period_days=None,
        metadata=None,
        statement_descriptor=None,
    ):
        """
        Create a new plan.

        API Documentation:
          https://stripe.com/docs/api#create_plan

        :param _id: Plan identifier
        :type _id: str
        :param name: Plan name
        :type name: str
        :param amount: Amount in cents to charge or 0 for a free plan
        :type amount: int
        :param currency: 3 digit currency abbreviation
        :type currency: str
        :param interval: Billing frequency
        :type interval: str
        :param interval_count: Number of intervals between each bill
        :type interval_count: int
        :param trial_period_days: Number of days to run a free trial
        :type trial_period_days: int
        :param metadata: Additional data to save with the plan
        :type metadata: dct
        :param statement_descriptor: Arbitrary string to appear on CC statement
        :type statement_descriptor: str
        :return: Stripe plan
        """
        try:
            return StripePlan.create(
                id=_id,
                name=name,
                amount=amount,
                currency=currency,
                interval=interval,
                interval_count=interval_count,
                trial_period_days=trial_period_days,
                metadata=metadata,
                statement_descriptor=statement_descriptor,
            )
        except StripeError as e:
            print(e)

    @classmethod
    def update(cls, id=None, name=None, metadata=None, statement_descriptor=None):
        """
        Update an existing plan.

        API Documentation:
          https://stripe.com/docs/api#update_plan

        :param id: Plan identifier
        :type id: str
        :param name: Plan name
        :type name: str
        :param metadata: Additional data to save with the plan
        :type metadata: dct
        :param statement_descriptor: Arbitrary string to appear on CC statement
        :type statement_descriptor: str
        :return: Stripe plan
        """
        try:
            plan = StripePlan.retrieve(id)

            plan.name = name
            plan.metadata = metadata
            plan.statement_descriptor = statement_descriptor

            return plan.save()
        except StripeError as e:
            print(e)

    @classmethod
    def delete(cls, plan):
        """
        Delete an existing plan.

        API Documentation:
          https://stripe.com/docs/api#delete_plan

        :param plan: Plan identifier
        :type plan: str
        :return: Stripe plan object
        """
        try:
            plan = StripePlan.retrieve(plan)

            return plan.delete()
        except StripeError as e:
            print(e)


class Event:
    @classmethod
    def retrieve(cls, event_id):
        """
        Retrieve an event, this is used to validate the event in attempt to
        protect us from potentially malicious events not sent from Stripe.

        API Documentation:
          https://stripe.com/docs/api#retrieve_event

        :param event_id: Stripe event id
        :type event_id: int
        :return: Stripe event
        """
        return StripeEvent.retrieve(event_id)


class Customer:
    @classmethod
    def create(cls, token=None, email=None, coupon=None, plan=None):
        """
        Create a new customer.

        API Documentation:
          https://stripe.com/docs/api#create_customer

        :param token: Token returned by JavaScript
        :type token: str
        :param email: E-mail address of the customer
        :type email: str
        :param coupon: Coupon code
        :type coupon: str
        :param plan: Plan identifier
        :type plan: str
        :return: Stripe customer
        """
        params = {"source": token, "email": email}

        if plan:
            params["plan"] = plan

        if coupon:
            params["coupon"] = coupon

        return StripeCustomer.create(**params)


class Charge:
    @classmethod
    def create(cls, customer_id=None, currency=None, amount=None):
        """
        Create a new charge.

        :param customer_id: Stripe customer id
        :type customer_id: int
        :param amount: Stripe currency
        :type amount: str
        :param amount: Amount in cents
        :type amount: int
        :return: Stripe charge
        """
        return StripeCharge.create(
            amount=amount,
            currency=currency,
            customer=customer_id,
            statement_descriptor="SNAKEEYES COINS",
        )
