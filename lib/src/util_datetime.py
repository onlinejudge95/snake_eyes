from datetime import date
from datetime import datetime
from datetime import timedelta

from pytz import utc


def tz_aware_datetime():
    """
    Utility to return a timezone aware date time object
    :return: Datetime
    """
    return datetime.now(utc)


def timedelta_month(months, compare_date=None):
    """
    Return a new date time object with a month's offset applied
    :param months: int Amount of month to offset
    :param compare_date: Date to compare at
    :return: datetime
    """
    if compare_date is None:
        compare_date = date.today()

    return compare_date + timedelta(months * 365 / 12)
