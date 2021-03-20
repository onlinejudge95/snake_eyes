from flask import Flask

from snake_eyes.blueprints.page import page_bp
from snake_eyes.extensions import debug_toolbar


def create_app(settings_override=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object("config.settings")
    app.config.from_pyfile("development.py")

    if settings_override:
        app.config.update(settings_override)

    app.register_blueprint(page_bp)

    init_extensioins(app)

    return app


def init_extensioins(app):
    """
    Registers extensions by lazy loading.
    This mutates the app object

    :param app: snake_eyes application isntance
    """
    debug_toolbar.init_app(app)
