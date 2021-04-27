from functools import wraps

from flask import flash
from flask import redirect
from flask_login import current_user


def anonymous_required(url="/settings"):
    """
    Redirect the user in case they are authenticated.

    :param url: URL to redirect to
    :type url: str
    :return: Function
    """

    def decorator(function):
        @wraps(function)
        def decorated_function(*args, **kwargs):
            if current_user.is_authenticated:
                return redirect(url)
            return function(*args, **kwargs)

        return decorated_function

    return decorator


def role_required(*roles):
    """
    Redirect the user if he is not authorized

    :param *roles: Roles that are allowed
    :return: Function
    """

    def decorator(function):
        @wraps(function)
        def decorated_function(*args, **kwargs):
            if current_user.role not in roles:
                flash("You are not authorized to take that action", "error")
                return redirect("/")
            return function(*args, **kwargs)

        return decorated_function

    return decorator
