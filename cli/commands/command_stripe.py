from click import argument
from click import command
from click import echo
from click import group

from snake_eyes.app import create_app
from snake_eyes.blueprints.billing.gateways.stripecom import (
    Plan as PaymentPlan,
)
from snake_eyes.extensions import db


app = create_app()
db.app = app


@group()
def cli():
    """
    Perform stripe tasks
    """
    pass


@command()
def sync():
    """
    Sync the plans to stripe
    """
    if app.config["STRIPE_PLANS"] is not None:
        for _, value in app.config["STRIPE_PLANS"].items():
            plan = PaymentPlan.retrieve(value.get("id"))

            if plan:
                PaymentPlan.update(
                    id=value.get("id"),
                    name=value.get("name"),
                    metadata=value.get("metadata"),
                    statement_descriptor=value.get("statement_descriptor"),
                )
            else:
                PaymentPlan.create(**value)


@command()
@argument("plan_ids", nargs=-1)
def delete(plan_ids):
    """
    Delete plans from stripe
    """
    for plan_id in plan_ids:
        PaymentPlan.delete(plan_id)


@command()
def show():
    """
    List all existing plans
    """
    echo(PaymentPlan.list())


cli.add_command(sync)
cli.add_command(delete)
cli.add_command(show)
