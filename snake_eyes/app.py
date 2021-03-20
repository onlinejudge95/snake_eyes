from flask import Flask

from snake_eyes.blueprints.page import page_bp


def create_app(settings_override=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object("config.settings")
    app.config.from_pyfile("development.py")

    if settings_override:
        app.config.update(settings_override)

    app.register_blueprint(page_bp)

    return app
