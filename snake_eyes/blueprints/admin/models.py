from sqlalchemy import func

from snake_eyes.blueprints.billing.models.subscription import Subscription
from snake_eyes.blueprints.bet.models.bet import Bet
from snake_eyes.blueprints.user.models import User
from snake_eyes.blueprints.user.models import db


class Dashboard:
    @classmethod
    def _group_and_count(cls, model, field):
        """
        Group results for a specific model and field

        :param model: Model to be used
        :type model: SQLAlchemy model
        :param field: Field for grouping
        :type field: SQLAlchemy field
        """
        count = func.count(field)
        query = db.session.query(count, field).group_by(field).all()

        return {"query": query, "total": model.query.count()}

    @classmethod
    def group_and_count_users(cls):
        """
        Perform a group by/count on all users
        :return: dict
        """
        return Dashboard._group_and_count(User, User.role)

    @classmethod
    def group_and_count_plans(cls):
        """
        Perform a group by/count on all plans
        :return: dict
        """
        return Dashboard._group_and_count(Subscription, Subscription.plan)

    @classmethod
    def group_and_count_coupons(cls):
        """
        Obtain coupon usage statistics across all subscribers.

        :return: tuple
        """
        count = db.session.query(Subscription) \
            .filter(Subscription.coupon.isnot(None)) \
            .count()
        total = db.session.query(func.count(Subscription.id)).scalar()

        percentage = 0 \
            if total == 0 else round((count / float(total)) * 100, 1)

        return count, total, percentage

    @classmethod
    def group_and_count_payouts(cls):
        """
        Performa  group by/count on all payouts.

        :return: dict
        """
        return Dashboard._group_and_count(Bet, Bet.payout)
