from sqlalchemy import func

from snake_eyes.blueprints.user.models import User
from snake_eyes.blueprints.user.models import db


class Dashboard:
    @classmethod
    def group_and_count_users(cls):
        """
        Perform a group and count on all users
        :return: dict
        """
        return Dashboard._group_and_count_users(User, User.role)

    @classmethod
    def _group_and_count_users(cls, model, field):
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
