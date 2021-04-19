from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CsrfProtect


db = SQLAlchemy()
debug_toolbar = DebugToolbarExtension()
login_manager = LoginManager()
mail = Mail()
csrf = CsrfProtect()
