from functools import wraps

from flask import flash
from flask import redirect
from flask import url_for
from flask_login import current_user


def coins_required(function):
    """
    Restrict access from users who have no coins.

    :return: Function
    """
    @wraps(function)
    def decorated_function(*args, **kwargs):
        if current_user.coins == 0:
            flash("Sorry, you're out of coins", "warning")
            return redirect(url_for("user.settings"))

        return function(*args, **kwargs)

    return decorated_function
