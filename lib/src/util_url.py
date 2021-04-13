from urllib.parse import urljoin

from flask import request


def safe_next_url(target_url):
    """
    Ensure a relative path is prefixed with the domain.
    Required for Flask-Login

    :param target_url: Relative URL
    :type target_url: str
    :return: str
    """
    return urljoin(request.host_url, target_url)
