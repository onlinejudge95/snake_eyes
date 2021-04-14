from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from sqlalchemy import text

from snake_eyes.blueprints.admin.forms import BulkDeleteForm
from snake_eyes.blueprints.admin.forms import SearchForm
from snake_eyes.blueprints.admin.forms import UserForm
from snake_eyes.blueprints.admin.models import Dashboard
from snake_eyes.blueprints.user.decorators import role_required
from snake_eyes.blueprints.user.models import User


bp = Blueprint(
    "admin",
    __name__,
    template_folder="templates",
    url_prefix="/admin"
)


@bp.before_request
@login_required
@role_required("admin")
def before_request():
    """
    Protects all admin endpoints
    """
    pass


@bp.route("")
def dashboard():
    group_and_count_users = Dashboard.group_and_count_users()
    return render_template(
        "admin/page/dashboard.html",
        group_and_count_users=group_and_count_users
    )


@bp.route("/users", defaults={"page": 1})
@bp.route("/users/page/<int:page>")
def users(page):
    search_form = SearchForm()
    bulk_form = BulkDeleteForm()

    sort_by = User.sort_by(
        request.args.get("sort", "created_on"),
        request.args.get("direction", "desc"),
    )
    order_values = f"{sort_by[0]} {sort_by[1]}"

    paginated_users = User.query \
        .filter(User.search(request.args.get("q", ""))) \
        .order_by(User.role.asc(), text(order_values)) \
        .paginate(page, 50, True)

    return render_template(
        "admin/user/index.html",
        form=search_form,
        bulk_form=bulk_form,
        users=paginated_users
    )


@bp.route("/users/bulk_delete", methods=["POST"])
def users_bulk_delete():
    form = BulkDeleteForm()

    if form.validate_on_submit():
        ids = User.get_bulk_action_ids(
            request.form.get("scope"),
            request.form.get("bulk_ids"),
            omit_ids=[current_user.id],
            query=request.args.get("q", "")
        )

        delete_count = User.bulk_delete(ids)

        flash(
            f"{delete_count} users(s) were scheduled for deletion",
            "success"
        )
    else:
        flash(
            "No users were deleted",
            "error"
        )

    return redirect(url_for("admin.users"))


@bp.route("/users/edit/<int:id>", methods=["GET", "POST"])
def users_edit(id):
    user = User.query.get(id)
    form = UserForm(obj=user)

    if form.validate_on_submit():
        if User.is_last_admin(
            user,
            request.form.get("role"),
            request.form.get("active")
        ):
            flash("You are the last admin, you cannot do that", "error")
            return redirect(url_for("admin.users"))

        form.populate_obj(user)

        if not user.username:
            user.username = None

        user.save()

        flash("User has been saved successfully", "success")
        return redirect(url_for("admin.users"))
    return render_template("admin/user/edit.html", form=form, user=user)
