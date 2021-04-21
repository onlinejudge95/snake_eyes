from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user

from lib.src.util_url import safe_next_url
from snake_eyes.blueprints.user.decorators import anonymous_required
from snake_eyes.blueprints.user.forms import BeginPasswordResetForm
from snake_eyes.blueprints.user.forms import LoginForm
from snake_eyes.blueprints.user.forms import PasswordResetForm
from snake_eyes.blueprints.user.forms import SignupForm
from snake_eyes.blueprints.user.forms import UpdateCredentials
from snake_eyes.blueprints.user.forms import UpdateLocaleForm
from snake_eyes.blueprints.user.forms import WelcomeForm
from snake_eyes.blueprints.user.models import User


bp = Blueprint("user", __name__, template_folder="templates")


@bp.route("/login", methods=["GET", "POST"])
@anonymous_required()
def login():
    form = LoginForm(next=request.args.get("next"))

    if form.validate_on_submit():
        user = User.find_by_identity(request.form.get("identity"))

        if user and user.authenticated(password=request.form.get("password")):
            if login_user(user, remember=True) and user.is_active():
                user.update_activity_tracking(request.remote_addr)

                next_url = request.form.get("next")
                if next_url:
                    return redirect(safe_next_url(next_url))
                return redirect(url_for("user.settings"))
            else:
                flash("The account is disabled", "error")
        else:
            flash("Identity or password is incorrect", "error")
    return render_template("user/login.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out", "success")
    return redirect(url_for("user.login"))


@bp.route("/account/begin_password_reset", methods=["GET", "POST"])
@anonymous_required()
def begin_password_reset():
    form = BeginPasswordResetForm()

    if form.validate_on_submit():
        user = User.initialize_password_reset(request.form.get("identity"))

        flash(
            f"An email with instructions have been sent to {user.email}",
            "success"
        )
        return redirect(url_for("user.login"))

    return render_template("user/begin_password_reset.html", form=form)


@bp.route("/account/password_reset", methods=["GET", "POST"])
@anonymous_required()
def password_reset():
    form = PasswordResetForm(reset_token=request.args.get("reset_token"))

    if form.validate_on_submit():
        user = User.deserialize_token(request.form.get("reset_token"))

        if user is None:
            flash("Your reset token has expired or tampered with", "error")
            return redirect(url_for("user.begin_password_reset"))

        form.populate_obj(user)
        user.password = User.encrypt_password(request.form.get("password"))
        user.save()

        if login_user(user):
            flash("Your password has been reset", "success")
            return redirect(url_for("user.settings"))

    return render_template("user/password_reset.html", form=form)


@bp.route("/signup", methods=["GET", "POST"])
@anonymous_required()
def signup():
    form = SignupForm()

    if form.validate_on_submit():
        user = User()

        form.populate_obj(user)

        user.password = User.encrypt_password(request.form.get("password"))
        user.save()

        if login_user(user):
            flash("Awesome, thanks for signing up", "success")
            return redirect(url_for("user.welcome"))

    return render_template("user/signup.html", form=form)


@bp.route("/welcome", methods=["GET", "POST"])
@login_required
def welcome():
    if current_user.username:
        flash("You have already picked a username", "warning")
        return redirect(url_for("user.settings"))

    form = WelcomeForm()

    if form.validate_on_submit():
        current_user.username = request.form.get("username")
        current_user.save()

        flash("Signup is complete", "success")
        return redirect(url_for("user.settings"))

    return render_template("user/welcome.html", form=form)


@bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    return render_template("user/settings.html")


@bp.route("/settings/update_credentials", methods=["GET", "POST"])
@login_required
def update_credentials():
    form = UpdateCredentials(current_user, uid=current_user.id)

    if form.validate_on_submit():
        new_password = request.form.get("password", "")
        current_user.email = request.form.get("email")

        if new_password:
            current_user.password = User.encrypt_password(new_password)

        current_user.save()

        flash("Your sign in settings are updated", "success")
        return redirect(url_for("user.settings"))

    return render_template("user/update_credentials.html", form=form)


@bp.route("/settings/update_locale", methods=["GET", "POST"])
@login_required
def update_locale():
    form = UpdateLocaleForm(locale=current_user.locale)

    if form.validate_on_submit():
        form.populate_obj(current_user)
        current_user.save()

        flash("Your locale settings have been updated", "success")
        return redirect(url_for("user.settings"))

    return render_template("user/update_locale.html", form=form)
