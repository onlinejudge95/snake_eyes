from flask import Flask

from snake_eyes.blueprints.page import page_bp


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object("config.settings")
    app.config.from_pyfile("development.py")

    app.register_blueprint(page_bp)

    @app.route("/health")
    def health():
        return {"status": "success"}

    return app
