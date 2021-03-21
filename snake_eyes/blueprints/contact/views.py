from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from snake_eyes.blueprints.contact.forms import ContactForm


bp = Blueprint("contact", __name__, template_folder="templates")


@bp.route("/contact", methods=["GET", "POST"])
def index():
    form = ContactForm()

    if form.validate_on_submit():
        from snake_eyes.blueprints.contact.tasks import deliver_contact_email

        print(request.form.get("email"), request.form.get("message"))

        deliver_contact_email.delay(request.form.get("email"), request.form.get("message"))

        flash("Thanks, expect a response shortly.", "success")
        return redirect(url_for("contact.index"))
    return render_template("contact/index.html", form=form)
