import datetime as dt
import pytz


def tz_aware_datetime():
    """
    Utility to return a timezone aware date time object
    :return: Datetime
    """
    return dt.datetime.now(pytz.utc)


def timedelta_month(months, compare_date=None):
    """
    Return a new date time object with a month's offset applied
    :param months: int Amount of month to offset
    :param compare_date: Date to compare at
    :return: datetime
    """
    if compare_date is None:
        compare_date = dt.datetime.today()

    delta = months * 365 / 12

    return compare_date + dt.timedelta(delta)
