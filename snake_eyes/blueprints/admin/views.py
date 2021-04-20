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
from snake_eyes.blueprints.admin.forms import CouponForm
from snake_eyes.blueprints.admin.forms import SearchForm
from snake_eyes.blueprints.admin.forms import UserCancelSubscriptionForm
from snake_eyes.blueprints.admin.forms import UserForm
from snake_eyes.blueprints.admin.models import Dashboard
from snake_eyes.blueprints.billing.decorators import handle_stripe_exceptions
from snake_eyes.blueprints.billing.models.coupon import Coupon
from snake_eyes.blueprints.billing.models.invoice import Invoice
from snake_eyes.blueprints.billing.models.subscription import Subscription
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
    group_and_count_coupons = Dashboard.group_and_count_coupons()
    group_and_count_payouts = Dashboard.group_and_count_payouts()
    group_and_count_plans = Dashboard.group_and_count_plans()
    group_and_count_users = Dashboard.group_and_count_users()
    return render_template(
        "admin/page/dashboard.html",
        group_and_count_coupons=group_and_count_coupons,
        group_and_count_plans=group_and_count_plans,
        group_and_count_users=group_and_count_users,
        group_and_count_payouts=group_and_count_payouts
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
        .order_by(User.role.asc(), User.payment_id, text(order_values)) \
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

        from snake_eyes.blueprints.billing.tasks import delete_users

        delete_users.delay(ids)

        flash(
            f"{len(ids)} users(s) were scheduled for deletion",
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

    invoices = Invoice.billing_history(current_user)

    upcoming = Invoice.upcoming(current_user.payment_id) \
        if current_user.subscription else None
    coupon = Coupon.query \
        .filter(Coupon.code == current_user.subscription.coupon).first() \
        if current_user.subscription else None

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
    print(form)
    return render_template(
        "admin/user/edit.html", form=form, user=user, invoices=invoices,
        upcoming=upcoming, coupon=coupon
    )


@bp.route("/users/cancel_subscription", methods=["POST"])
def users_cancel_subscription():
    form = UserCancelSubscriptionForm()

    if form.validate_on_submit():
        user = User.query.get(request.form.get("id"))

        if user:
            subscription = Subscription()
            if subscription.cancel(user):
                flash(
                    f"Subscription has been cancelled for {user.name}",
                    "success"
                )
        else:
            flash(
                "No subscription was cancelled, something went wrong",
                "error"
            )

    return redirect(url_for("admin.users"))


@bp.route("/coupons", defaults={"page": 1})
@bp.route("/coupons/page/<int:page>")
def coupons(page):
    search_form = SearchForm()
    bulk_form = BulkDeleteForm()

    sort_by = Coupon.sort_by(
        request.args.get("sort", "created_on"),
        request.args.get("direction", "desc"),
    )
    order_values = f"{sort_by[0]} {sort_by[1]}"

    paginated_coupons = Coupon.query \
        .filter(Coupon.search(request.args.get("q", ""))) \
        .order_by(text(order_values)) \
        .paginate(page, 50, True)

    return render_template(
        "admin/coupon/index.html", form=search_form, bulk_form=bulk_form,
        coupons=paginated_coupons
    )


@bp.route("/coupons/new", methods=["GET", "POST"])
@handle_stripe_exceptions
def coupons_new():
    coupon = Coupon()
    form = CouponForm(obj=coupon)

    if form.validate_on_submit():
        form.populate_obj(coupon)

        params = {
            "code": coupon.code,
            "duration": coupon.duration,
            "percent_off": coupon.percent_off,
            "amount_off": coupon.amount_off,
            "currency": coupon.currency,
            "redeem_by": coupon.redeem_by,
            "max_redemptions": coupon.max_redemptions,
            "duration_in_months": coupon.duration_in_months
        }

        if Coupon.create(params):
            flash("Coupon has been created successfully", "success")
            return redirect(url_for("admin.coupons"))
    return render_template("admin/coupon/new.html", form=form, coupon=coupon)


@bp.route("/coupons/bulk_delete", methods=["POST"])
def coupons_bulk_delete():
    form = BulkDeleteForm()

    if form.validate_on_submit():
        ids = Coupon.get_bulk_action_ids(
            request.form.get("scope"),
            request.form.getlist("bulk_ids"),
            query=request.args.get("q", "")
        )

        from snake_eyes.blueprints.billing.tasks import delete_coupons

        delete_coupons.delay(ids)
        flash(f"{len(ids)} coupons(s) were scheduled to be deleted", "success")
    else:
        flash("No coupons were deleted, something went wrong", "error")

    return redirect(url_for("admin.coupons"))
