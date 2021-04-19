from snake_eyes.app import create_celery
from snake_eyes.blueprints.billing.models.coupon import Coupon
from snake_eyes.blueprints.billing.models.credit_card import CreditCard
from snake_eyes.blueprints.user.models import User


celery = create_celery()


@celery.task()
def mark_old_credit_cards():
    """
    Mark credit cards that are going to expire soon or have expired.

    :return: Result of updating the records
    """
    return CreditCard.mark_old_credit_cards()


@celery.task()
def expire_old_coupons():
    """
    Invalidate coupons that are past their redeem date.

    :return: Result of updating the records
    """
    return Coupon.expire_old_coupons()


@celery.task()
def delete_users(ids):
    """
    Delete users and potentially cancel their subscription.

    :param ids: List of ids to be deleted
    :type ids: list
    :return: int
    """
    return User.bulk_delete(ids)


@celery.task()
def delete_coupons(ids):
    """
    Delete coupons both on the payment gateway and locally.

    :param ids: List of ids to be deleted
    :type ids: list
    :return: int
    """
    return Coupon.bulk_delete(ids)
