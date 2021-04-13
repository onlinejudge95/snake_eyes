import datetime

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
        if isinstance(value, datetime.datetime) and value.tzinfo is None:
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

    def save(self):
        """
        Save a model instance to db
        """
        db.session.add(self)
        db.session.commit()

        return self

    def delete(self):
        """
        Delete a model instance to db
        """
        db.session.delete(self)
        db.session.commit()

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
