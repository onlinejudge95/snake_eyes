from logging import ERROR
from logging import Formatter
from logging.handlers import SMTPHandler

import stripe

from celery import Celery
from flask import Flask
from flask import render_template
from flask import request
from flask_login import current_user
from itsdangerous import URLSafeTimedSerializer
from werkzeug.contrib.fixers import ProxyFix

from snake_eyes.blueprints.admin import admin_bp
from snake_eyes.blueprints.bet import bet_bp
from snake_eyes.blueprints.billing import billing_bp
from snake_eyes.blueprints.billing import stripe_webhook_bp
from snake_eyes.blueprints.billing.template_processors import current_year
from snake_eyes.blueprints.billing.template_processors import format_currency
from snake_eyes.blueprints.contact import contact_bp
from snake_eyes.blueprints.page import page_bp
from snake_eyes.blueprints.user import user_bp
from snake_eyes.blueprints.user.models import User
from snake_eyes.extensions import babel
from snake_eyes.extensions import csrf
from snake_eyes.extensions import db
from snake_eyes.extensions import limiter
from snake_eyes.extensions import login_manager
from snake_eyes.extensions import mail


def create_app(settings_override=None):
    """
    Create a Flask application using the app factory pattern.

    :param settings_override: Override settings
    :return: Flask app
    """
    app = Flask(__name__)

    app.config.from_object("config.settings")

    if settings_override:
        app.config.update(settings_override)

    app.logger.setLevel(app.config["LOG_LEVEL"])

    stripe.api_key = app.config.get("STRIPE_SECRET_KEY")
    stripe.api_version = app.config.get("STRIPE_API_VERSION")

    middleware(app)
    error_handler(app)
    exception_handler(app)

    app.register_blueprint(page_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(billing_bp)
    app.register_blueprint(stripe_webhook_bp)
    app.register_blueprint(bet_bp)

    template_processors(app)
    init_extensions(app)
    authentication(app, User)
    locale(app)

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
        include=app.config["CELERY_TASK_LIST"],
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
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    babel.init_app(app)


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


def middleware(app):
    """
    Registers the given middlewares.

    :param app: Flask app instance
    """
    app.wsgi_app = ProxyFix(app.wsgi_app)


def error_handler(app):
    """
    Regsiter custom error handler on app level

    :param app: Flask app instance
    """

    def render_status(status):
        """
        Render custom tempaltes for specific errors

        :param status: Status to show
        :type status: str
        """
        status_code = getattr(status, "code", 500)
        return render_template(f"errors/{status_code}.html"), status_code

    for error in [404, 429, 500]:
        app.errorhandler(error)(render_status)


def exception_handler(app):
    """
    Regsiter custom exception handler on app level

    :param app: Flask app instance
    """
    mail_handler = SMTPHandler(
        (app.config.get("MAIL_SERVER"), app.config.get("MAIL_PORT")),
        app.config.get("MAIL_USERNAME"),
        [app.config.get("MAIL_USERNAME")],
        "[Exception Handler] A 5xx was thrown",
        (app.config.get("MAIL_USERNAME"), app.config.get("MAIL_PASSWORD")),
        secure=(),
    )
    mail_handler.setLevel(ERROR)
    mail_handler.setFormatter(
        Formatter(
            """
            Time        : %(asctime)s
            Message Type: %(levelname)s

            Message:

            %(message)s
            """
        )
    )
    app.logger.addHandler(mail_handler)


def template_processors(app):
    """
    Register custom template processors

    :param app: Flask app instance
    :return: App jinja environment
    """
    app.jinja_env.filters["format_currency"] = format_currency
    app.jinja_env.globals.update(current_year=current_year)

    return app.jinja_env


def locale(app):
    """
    Initialize a locale for the current request.

    :param app: Flask application instance
    :return: str
    """

    @babel.localeselector
    def get_locale():
        if current_user.is_authenticated:
            return current_user.locale

        return request.accept_languages.best_match(app.config.get("LANGUAGES").keys())
