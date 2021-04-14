from collections import OrderedDict
from datetime import datetime
from hashlib import md5

from flask import current_app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer
from itsdangerous import URLSafeTimedSerializer
from pytz import utc
from sqlalchemy import or_
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from lib.src.util_sqlalchemy import AwareDateTime, ResourceMixin
from snake_eyes.extensions import db


class User(UserMixin, ResourceMixin, db.Model):
    __tablename__ = "users"

    ROLE = OrderedDict([
        ("member", "Member"),
        ("admin", "Admin"),
    ])

    id = db.Column(db.Integer, primary_key=True)

    # Attributes for authetication
    role = db.Column(
        db.Enum(*ROLE, name="role_types", native_enum=False),
        index=True,
        nullable=False,
        server_default="member"
    )
    active = db.Column(
        "is_active",
        db.Boolean(),
        nullable=False,
        server_default="1"
    )
    username = db.Column(db.String(24), unique=True, index=True)
    email = db.Column(
        db.String(255),
        unique=True,
        index=True,
        nullable=False,
        server_default=""
    )
    password = db.Column(db.String(128), nullable=False, server_default="")

    # Attributes for activity tracking
    sign_in_count = db.Column(db.Integer, nullable=False, default=0)
    current_sign_in_on = db.Column(AwareDateTime())
    current_sign_in_ip = db.Column(db.String(45))
    last_sign_in_on = db.Column(AwareDateTime())
    last_sign_in_ip = db.Column(db.String(45))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

        self.password = User.encrypt_password(kwargs.get("password", ""))

    @classmethod
    def find_by_identity(cls, identity):
        """
        Find a user by their email or user name
        :param identity: Email or username
        :type identity: str
        :return: User or None
        """
        return User.query.filter(
            (User.email == identity) | (User.username == identity)
        ).first()

    @classmethod
    def encrypt_password(cls, plaintext_password):
        """
        Hash a plaintext string using PBKDF2.
        :param plaintext_password: Password to encrypt
        :type plaintext_password: str
        :return: str
        """
        if plaintext_password:
            return generate_password_hash(plaintext_password)

    @classmethod
    def deserialize_token(cls, token):
        """
        Deserialize a web token to provide a user instance
        :param token: Signed token
        :type token: str
        :return: User or None
        """
        private_key = TimedJSONWebSignatureSerializer(
            current_app.config["SECRET_KEY"]
        )

        try:
            decoded_payload = private_key.loads(token)

            return User.find_by_identity(decoded_payload.get("user_email"))
        except Exception:
            return None

    @classmethod
    def initialize_password_reset(cls, identity):
        """
        Generate password reset token for a user
        :param identity: Email or username
        :type identity: str
        :return: User or None
        """
        user = User.find_by_identity(identity)
        reset_token = user.serialize_token()

        from snake_eyes.blueprints.user.tasks import deliever_password_reset_mail  # noqa: E501
        deliever_password_reset_mail.delay(user.id, reset_token)

        return user

    @classmethod
    def search(cls, query):
        """
        Search a resource by one or more fields
        :param query: Search query
        :type query: str
        return: SQLAlchemy filter
        """
        if not query:
            return ""

        search_query = f"%{query}%"
        search_chain = (
            User.email.ilike(search_query),
            User.username.ilike(search_query)
        )

        return or_(*search_chain)

    @classmethod
    def is_last_admin(cls, user, new_role, new_active):
        """
        Checks if this user is the last admin.
        Last admin can not remove themselves from the admins list.

        :param user: User being tested
        :type user: User
        :param new_role: New role being set
        :type new_role: str
        :param new_active: New active status being set
        :type new_active: bool
        :return: bool
        """
        is_changing_roles = user.role == "admin" and new_role != "admin"
        is_changing_active = user.active is True and new_active is None

        if is_changing_roles or is_changing_active:
            admin_count = User.query.filter(User.role == "admin").count()
            active_count = User.query.filter(User.is_active is True).count()

            if admin_count == 1 or active_count == 1:
                return True

        return False

    def is_active(self):
        """
        Return if the user account is active.
        Required for Flask-Login

        :return: bool
        """
        return self.active

    def get_auth_token(self):
        """
        Return the user's auth token.
        This should be invalidated if the user changes their password.
        We can use md5 as no info leak happens here.
        Required by Flask-Login.

        :return: str
        """
        private_key = current_app.config["SECRET_KEY"]
        serializer = URLSafeTimedSerializer(private_key)

        data = [str(self.id), md5(self.password.encode("utf-8")).hexdigest()]

        return serializer.dumps(data)

    def authenticated(self, with_password=True, password=""):
        """
        Ensure that the user is authenticated and
        optionally check their password.
        :param with_password: Flag to check the password
        :type with_password: bool
        :param password: Password to check against
        :type password: str
        :return: bool
        """
        if with_password:
            return check_password_hash(self.password, password)

        return True

    def serialize_token(self, expiration=3600):
        """
        Create and sign a token for the user to have access
        :param expiration: Seconds untill the token's expiry
        :type expiration: int
        :return: JSON
        """
        private_key = current_app.config["SECRET_KEY"]
        serializer = TimedJSONWebSignatureSerializer(private_key, expiration)

        return serializer.dumps({"user_email": self.email}).decode("utf-8")

    def update_activity_tracking(self, ip_address):
        """
        Update fields for user activity tracking

        :param ip_address: IP addresss of the user
        :type ip_address: str
        :return: SQLAlchemy commit results
        """
        self.sign_in_count += 1

        self.last_sign_in_ip = self.current_sign_in_ip
        self.last_sign_in_on = self.current_sign_in_on

        self.current_sign_in_ip = ip_address
        self.current_sign_in_on = datetime.now(utc)

        return self.save()
