from flask import Blueprint
from flask import render_template


bp = Blueprint("page", __name__, template_folder="templates")


@bp.route("/")
def home():
    return render_template("page/home.html")

@bp.route("/privacy")
def privacy():
    return render_template("page/privacy.html")


@bp.route("/terms")
def terms():
    return render_template("page/terms.html")
