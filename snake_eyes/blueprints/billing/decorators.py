from functools import wraps

from flask import flash
from flask import redirect
from flask import url_for
from flask_login import current_user
from stripe.error import APIConnectionError
from stripe.error import AuthenticationError
from stripe.error import CardError
from stripe.error import InvalidRequestError
from stripe.error import StripeError


def handle_stripe_exceptions(function):
    """
    Handle Stripe exceptions so they do not throw 500s.

    :param function: Function to decorate
    :type function: Function
    :return: Function
    """

    @wraps(function)
    def decorated_function(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except CardError:
            flash("Sorry, the card was declined. Try again perhaps?", "error")
            return redirect(url_for("user.settings"))
        except InvalidRequestError as e:
            flash(e, "error")
            return redirect(url_for("user.settings"))
        except AuthenticationError:
            flash("Authentication with our payment gateway failed", "error")
            return redirect(url_for("user.settings"))
        except APIConnectionError:
            flash("Our payment gateway is having connectivity issues", "error")
            return redirect(url_for("user.settings"))
        except StripeError:
            flash("Our payment gateway is having issues, please try again.", "error")
            return redirect(url_for("user.settings"))

    return decorated_function


def subscription_required(function):
    """
    Ensure a user is subscribed, if not redirect them to the pricing table.

    :return: Function
    """

    @wraps(function)
    def decorated_function(*args, **kwargs):
        if not current_user.subscription:
            return redirect(url_for("billing.pricing"))

        return function(*args, **kwargs)

    return decorated_function
