from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.types import TypeDecorator

from lib.src.util_datetime import tz_aware_datetime
from snake_eyes.extensions import db


class AwareDateTime(TypeDecorator):
    """
    Time zone aware utility for storing date time objects
    """
    impl = DateTime(timezone=True)

    def process_bind_param(self, value, dialect):
        if isinstance(value, datetime) and value.tzinfo is None:
            raise ValueError(f"{value} must be time zone aware")
        return value


class ResourceMixin:
    """
    Mixin for managing db objects
    """
    created_on = db.Column(AwareDateTime(), default=tz_aware_datetime)
    updated_on = db.Column(
        AwareDateTime(),
        default=tz_aware_datetime,
        onupdate=tz_aware_datetime
    )

    @classmethod
    def sort_by(cls, field, direction):
        """
        Validate the sort field and sort direction
        :param field: Field to sort on
        :type field: str
        :param direction: Sort direction
        :type direction: str
        :return: tuple
        """
        if field not in cls.__table__.columns:
            field = "created_on"

        if direction not in ("asc", "desc"):
            direction = "asc"

        return field, direction

    @classmethod
    def get_bulk_action_ids(cls, scope, ids, omit_ids=[], query=""):
        """
        Determine which ids are to be modified

        :param scope: Affect all or only a subset of items
        :type scope: str
        :param ids: List of ids to be modified
        :type ids: list
        :param omit_ids: Remove one or more IDs from the list
        :type omit_ids: list
        :param query: Search query (if applicable)
        :type query: str
        :return: list
        """
        omit_ids = list(map(str, omit_ids))

        if scope == "all_search_results":
            ids = [
                str(item[0])
                for item in cls.query.with_entities(cls.id)
                .filter(cls.search(query))
            ]

        if omit_ids:
            ids = [_id for _id in ids if _id not in omit_ids]

        return ids

    @classmethod
    def bulk_delete(cls, ids):
        """
        Bulk delete model instances

        :param ids: List of ids to be deleted
        :type ids: list
        :return: int
        """
        delete_count = cls.query \
            .filter(cls.id.in_(ids)) \
            .delete(synchronize_session=False)
        db.session.commit()

        return delete_count

    def save(self):
        """
        Save a model instance to db
        """
        db.session.add(self)
        db.session.commit()

        return self

    def delete(self):
        """
        Delete a model instance in db
        """
        db.session.delete(self)
        return db.session.commit()

    def __str__(self):
        """
        Return a readbale version of instance
        """
        obj_id = hex(id(self))
        columns = self.__table__.c.keys()

        values = ", ".join([
            f"{column}={getattr(self, column)}" for column in columns
        ])

        return f"<{obj_id} {self.__class__.__name__}({values})>"
