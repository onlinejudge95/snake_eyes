from celery import Celery
from flask import Flask
from itsdangerous import URLSafeTimedSerializer

from snake_eyes.blueprints.page import page_bp
from snake_eyes.blueprints.contact import contact_bp
from snake_eyes.blueprints.user import user_bp
from snake_eyes.blueprints.user.models import User
from snake_eyes.extensions import db
from snake_eyes.extensions import debug_toolbar
from snake_eyes.extensions import login_manager
from snake_eyes.extensions import mail
from snake_eyes.extensions import csrf


def create_app(settings_override=None):
    """
    Create a Flask application using the app factory pattern.

    :param settings_override: Override settings
    :return: Flask app
    """
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object("config.settings")
    app.config.from_pyfile("development.py", silent=True)

    if settings_override:
        app.config.update(settings_override)

    app.register_blueprint(page_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(user_bp)

    init_extensions(app)
    authentication(app, User)

    return app


def create_celery(app=None):
    """
    Create a new Celery object and tie together the Celery config to the app's
    config. Wrap all tasks in the context of the application.

    :param app: Flask app
    :return: Celery app
    """
    app = app or create_app()

    celery = Celery(
        app.import_name,
        broker=app.config["CELERY_BROKER_URL"],
        include=app.config["CELERY_TASK_LIST"]
    )
    celery.conf.update(app.config)

    BaseTask = celery.Task

    class ContextTask(BaseTask):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return BaseTask.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


def init_extensions(app):
    """
    Registers extensions by lazy loading.
    This mutates the app object

    :param app: Flask application isntance
    """
    db.init_app(app)
    debug_toolbar.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)


def authentication(app, user_model):
    """
    Initialization requied for Flask-Login.

    :param app: Flask app instance
    :param user_model: Model with auth information
    """
    login_manager.login_view = "user.login"

    @login_manager.user_loader
    def load_user(uid):
        return user_model.query.get(uid)

    @login_manager.token_loader
    def load_token(token):
        duration = app.config["REMEMBER_COOKIE_DURATION"].total_seconds()
        serializer = URLSafeTimedSerializer(app.secret_key)

        data = serializer.loads(token, max_age=duration)
        user_uid = data[0]

        return user_model.query.get(user_uid)
