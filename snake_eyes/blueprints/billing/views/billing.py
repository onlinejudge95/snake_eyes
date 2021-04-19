from flask import Blueprint
from flask import current_app
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required

from config import settings
from lib.src.util_json import render_json
from snake_eyes.blueprints.billing.decorators import handle_stripe_exceptions
from snake_eyes.blueprints.billing.decorators import subscription_required
from snake_eyes.blueprints.billing.forms import CancelSubscriptionForm
from snake_eyes.blueprints.billing.forms import CreditCardForm
from snake_eyes.blueprints.billing.forms import UpdateSubscriptionForm
from snake_eyes.blueprints.billing.models.coupon import Coupon
from snake_eyes.blueprints.billing.models.invoice import Invoice
from snake_eyes.blueprints.billing.models.subscription import Subscription


bp = Blueprint(
    "billing",
    __name__,
    template_folder="../templates",
    url_prefix="/subscription"
)


@bp.route("/pricing")
def pricing():
    if current_user.is_authenticated and current_user.subscription:
        return redirect(url_for("billing.update"))

    form = UpdateSubscriptionForm()

    return render_template(
        "billing/pricing.html", form=form, plans=settings.STRIPE_PLANS
    )


@bp.route("/coupon_code", methods=["POST"])
@login_required
def coupon_code():
    code = request.form.get("coupon_code")

    if code is None:
        return render_json(422, {"error": "Coupon code can not be processed"})

    coupon = Coupon.find_by_code(code)

    return render_json(404, {"error": "Coupon code not found"}) \
        if coupon is None else \
        render_json(200, {"data": coupon.to_json()})


@bp.route("/create", methods=["GET", "POST"])
@login_required
@handle_stripe_exceptions
def create():
    if current_user.subscription:
        flash("You already have an active subscriptions", "info")
        return redirect(url_for("user.settings"))

    plan = request.args.get("plan")
    subscription_plan = Subscription.get_plan_by_id(plan)

    if subscription_plan is None and request.method == "GET":
        flash("Sorry the plan does not exists", "error")
        return redirect(url_for("billing.pricing"))

    stripe_key = current_app.config.get("STRIPE_PUBLISHABLE_KEY")
    form = CreditCardForm(stripe_key=stripe_key, plan=plan)

    if form.validate_on_submit():
        subscription = Subscription()
        created = subscription.create(
            user=current_user, name=request.form.get("name"),
            plan=request.form.get("plan"),
            coupon=request.form.get("coupon_code"),
            token=request.form.get("stripe_token")
        )

        if created:
            flash("Awesome, thanks for subscribing", "success")
        else:
            flash("You must enable Javascript for this", "warning")

        return redirect(url_for("user.settings"))

    return render_template(
        "billing/payment_method.html", form=form, plan=subscription_plan
    )


@bp.route("/update", methods=["GET", "POST"])
@login_required
@handle_stripe_exceptions
@subscription_required
def update():
    current_plan = current_user.subscription.plan
    active_plan = Subscription.get_plan_by_id(current_plan)
    new_plan = Subscription.get_new_plan(request.form.keys())

    plan = Subscription.get_plan_by_id(new_plan)

    is_same_plan = new_plan == active_plan["id"]
    if (new_plan is not None and plan is None) or is_same_plan:
        if request.method == "POST":
            return redirect(url_for("billing.update"))

    form = UpdateSubscriptionForm(
        coupon_code=current_user.subscription.coupon
    )

    if form.validate_on_submit():
        subscription = Subscription()
        updated = subscription.update(
            user=current_user, coupon=request.form.get("coupon_code"),
            plan=plan.get("id")
        )

        if updated:
            flash("Your subscription has been updated", "success")
            return redirect(url_for("user.settings"))

    return render_template(
        "billing/pricing.html", form=form, plans=settings.STRIPE_PLANS,
        active_plan=active_plan
    )


@bp.route("/cancel", methods=["GET", "POST"])
@login_required
@handle_stripe_exceptions
def cancel():
    if not current_user.subscription:
        flash("You do not have an active subscription", "error")
        return redirect(url_for("user.settings"))

    form = CancelSubscriptionForm()

    if form.validate_on_submit():
        subscription = Subscription()
        cancelled = subscription.cancel(user=current_user)

        if cancelled:
            flash(
                "Sorry to see you go, your subscription has been cancelled",
                "success"
            )
            return redirect(url_for("user.settings"))

    return render_template("billing/cancel.html", form=form)


@bp.route("/update_payment_method", methods=["GET", "POST"])
@login_required
@handle_stripe_exceptions
def update_payment_method():
    if not current_user.credit_card:
        flash("You do not have a payment method added", "error")
        return redirect(url_for("user.settings"))

    active_plan = Subscription.get_plan_by_id(current_user.subscription.plan)
    card = current_user.credit_card

    form = CreditCardForm(
        stripe_key=current_app.config.get("STRIPE_PUBLISHABLE_KEY"),
        plan=active_plan, name=current_user.name
    )

    if form.validate_on_submit():
        subscription = Subscription()
        updated = subscription.update_payment_method(
            user=current_user, credit_card=card,
            name=request.form.get("name"),
            token=request.form.get("stripe_token")
        )

        if updated:
            flash("Your payment method has been updated", "success")
        else:
            flash("You must enable JavaScript for this request", "warning")

        return redirect(url_for("user.settings"))

    return render_template(
        "billing/payment_method.html", form=form, plan=active_plan,
        card_last4=str(card.last4)
    )


@bp.route("/billing_details")
@login_required
@handle_stripe_exceptions
def billing_details():
    invoices = Invoice.billing_history(current_user)

    upcoming = Invoice.upcoming(current_user.payment_id) \
        if current_user.subscription else None
    coupon = Coupon.query \
        .filter(Coupon.code == current_user.subscription.coupon).first() \
        if current_user.subscription else None

    return render_template(
        "billing/billing_details.html", invoices=invoices, upcoming=upcoming,
        coupon=coupon
    )
