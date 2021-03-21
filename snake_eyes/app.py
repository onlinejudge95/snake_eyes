from celery import Celery
from flask import Flask

from snake_eyes.blueprints.page import page_bp
from snake_eyes.blueprints.contact import contact_bp
from snake_eyes.extensions import debug_toolbar
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
    app.config.from_pyfile("development.py")

    if settings_override:
        app.config.update(settings_override)

    app.register_blueprint(page_bp)
    # app.register_blueprint(contact_bp, url_prefix="/contact")
    app.register_blueprint(contact_bp)

    init_extensioins(app)

    return app


def create_celery(app=None):
    """
    Create a new Celery object and tie together the Celery config to the app's
    config. Wrap all tasks in the context of the application.

    :param app: Flask app
    :return: Celery app
    """
    app = app or create_app()

    celery = Celery(app.import_name, broker=app.config["CELERY_BROKER_URL"], include=app.config["CELERY_TASK_LIST"])
    celery.conf.update(app.config)

    BaseTask = celery.Task

    class ContextTask(BaseTask):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return BaseTask.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


def init_extensioins(app):
    """
    Registers extensions by lazy loading.
    This mutates the app object

    :param app: Flask application isntance
    """
    debug_toolbar.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
