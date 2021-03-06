from flask import Blueprint
from flask import request
from stripe.error import InvalidRequestError

from lib.src.util_json import render_json
from snake_eyes.blueprints.billing.gateways.stripecom import (
    Event as PaymentEvent,
)
from snake_eyes.blueprints.billing.models.invoice import Invoice
from snake_eyes.blueprints.billing.models.subscription import Subscription
from snake_eyes.extensions import csrf


bp = Blueprint("stripe_webhook", __name__, url_prefix="/stripe_webhook")


@bp.route("/event", methods=["POST"])
@csrf.exempt
def event():
    if not request.json:
        return render_json(406, {"error": "Mime-Type is not application/json"})

    if request.json.get("id") is None:
        return render_json(406, {"error": "Invalid stripe event"})

    try:
        safe_event = PaymentEvent.retrieve(request.json.get("id"))
        parsed_event = Invoice.parse_from_event(safe_event)

        user = Invoice.prepare_and_save(parsed_event)

        if parsed_event.get("total") > 0:
            plan = Subscription.get_plan_by_id(user.subscription.plan)
            user.add_coins(plan)
    except InvalidRequestError as e:
        return render_json(422, {"error": str(e)})
    except Exception as e:
        return render_json(200, {"error": str(e)})

    return render_json(200, {"success": True})
