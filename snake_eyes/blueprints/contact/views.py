from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user

from snake_eyes.blueprints.contact.forms import ContactForm


bp = Blueprint("contact", __name__, template_folder="templates")


@bp.route("/contact", methods=["GET", "POST"])
def index():
    form = ContactForm(obj=current_user)

    if form.validate_on_submit():
        from snake_eyes.blueprints.contact.tasks import deliver_contact_email

        deliver_contact_email.delay(
            request.form.get("email"), request.form.get("message")
        )

        flash("Thanks, expect a response shortly.", "success")
        return redirect(url_for("contact.index"))
    return render_template("contact/index.html", form=form)
