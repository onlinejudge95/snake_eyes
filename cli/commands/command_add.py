from datetime import datetime
from random import choice
from random import randint
from random import random

from click import command
from click import echo
from click import group
from click import pass_context
from faker import Faker

from snake_eyes.app import create_app
from snake_eyes.blueprints.bet.models.bet import Bet
from snake_eyes.blueprints.bet.models.dice import roll
from snake_eyes.blueprints.billing.models.invoice import Invoice
from snake_eyes.blueprints.user.models import User
from snake_eyes.extensions import db


app = create_app()
db.app = app
faker = Faker()


def _log_status(count, model_label):
    """
    Log the output of records creation

    :param count: Count of created users
    :type count: int
    :param model_label: Name of the model
    :type model_label: str
    """
    echo(f"Created {count} {model_label}")


def _bulk_insert(model, data, label):
    """
    Bulk insert data to a model and log it.

    :param model: Model to use
    :type model: SQLAlchemy model
    :param data: Data to be saved
    :type data: list
    :param label: Label for the output
    :type label: str
    """
    with app.app_context():
        model.query.delete()
        db.session.commit()
        db.engine.execute(model.__table__.insert(), data)

        _log_status(model.query.count(), label)


@group()
def cli():
    """
    Add items to the db
    """
    pass


@command()
def users():
    """
    Generate fake users
    """
    data = []

    echo("Working...")

    random_emails = [faker.email() for i in range(99)]
    random_emails.append(app.config["SEED_ADMIN_EMAIL"])
    random_emails = list(set(random_emails))

    while True:
        if len(random_emails) == 0:
            break

        fake_datetime = faker \
            .date_time_between(start_date="-1y", end_date="now") \
            .strftime("%s")
        created_on = datetime \
            .utcfromtimestamp(float(fake_datetime)) \
            .strftime("%Y-%m-%dT%H:%M:%S Z")
        fake_datetime = faker \
            .date_time_between(start_date="-1y", end_date="now") \
            .strftime("%s")
        current_sign_in_on = datetime \
            .utcfromtimestamp(float(fake_datetime)) \
            .strftime("%Y-%m-%dT%H:%M:%S Z")

        role = "member" if random() >= 0.05 else "admin"
        random_trail = str(int(round((random() * 1000))))
        first_name = faker.first_name()
        username = f"{first_name}{random_trail}" if random() >= 0.05 else None
        last_bet_on = created_on if random() >= 0.5 else None

        email = random_emails.pop()

        params = {
            "created_on": created_on,
            "updated_on": created_on,
            "role": role,
            "email": email,
            "username": username,
            "password": User.encrypt_password("password"),
            "sign_in_count": random() * 100,
            "coins": 100,
            "last_bet_on": last_bet_on,
            "current_sign_in_on": current_sign_in_on,
            "current_sign_in_ip": faker.ipv4(),
            "last_sign_in_on": current_sign_in_on,
            "last_sign_in_ip": faker.ipv4()
        }

        if email == app.config["SEED_ADMIN_EMAIL"]:
            params["role"] = "admin"
            params["password"] = User.encrypt_password(
                app.config["SEED_ADMIN_PASSWORD"]
            )

        data.append(params)

    return _bulk_insert(User, data, "users")


@command()
def invoices():
    """
    Generate fake invoices
    """
    data = []

    for user in db.session.query(User).all():
        for i in range(randint(1, 12)):
            fake_created_on = faker \
                .date_time_between(start_date="-1y", end_date="now") \
                .strftime("%s")
            created_on = datetime \
                .utcfromtimestamp(float(fake_created_on)) \
                .strftime("%Y-%m-%dT%H:%M:%S Z")

            fake_period_start_on = faker \
                .date_time_between(start_date="now", end_date="+1y") \
                .strftime("%s")
            period_start_on = datetime \
                .utcfromtimestamp(float(fake_period_start_on)) \
                .strftime("%Y-%m-%d")

            fake_period_end_on = faker \
                .date_time_between(
                    start_date=period_start_on, end_date="+14d"
                ) \
                .strftime("%s")
            period_end_on = datetime \
                .utcfromtimestamp(float(fake_period_end_on)) \
                .strftime("%Y-%m-%d")

            fake_exp_date = faker \
                .date_time_between(start_date="now", end_date="+2y") \
                .strftime("%s")
            exp_date = datetime \
                .utcfromtimestamp(float(fake_exp_date)) \
                .strftime("%Y-%m-%d")

            plans = ["BRONZE", "GOLD", "PLATINUM"]
            cards = ["Visa", "Mastercard", "AMEX", "J.C.B", "Diner's Club"]

            params = {
                "created_on": created_on,
                "updated_on": created_on,
                "user_id": user.id,
                "receipt_number": faker.md5(),
                "description": f"{choice(plans)} MONTHLY",
                "period_start_on": period_start_on,
                "period_end_on": period_end_on,
                "currency": "usd",
                "tax": random() * 100,
                "tax_percent": random() * 10,
                "total": random() * 1000,
                "brand": choice(cards),
                "last4": randint(1000, 9000),
                "exp_date": exp_date
            }
            data.append(params)

    return _bulk_insert(Invoice, data, "invoices")


@command()
def bets():
    """
    Generate random bets.
    """
    data = []

    for user in db.session.query(User).all():
        for i in range(randint(10, 20)):
            fake_datetime = faker \
                .date_time_between(start_date="-1y", end_date="now") \
                .strftime("%s")
            created_on = datetime \
                .utcfromtimestamp(float(fake_datetime)) \
                .strftime("%Y-%m-%dT%H:%M:%S Z")

            wagered = randint(1, 100)
            dice_1, dice_2 = roll(), roll()
            outcome = dice_1 + dice_2

            guess = outcome if random() >= 0.75 else randint(2, 12)

            is_winner = Bet.is_winner(guess, outcome)
            payout = Bet.determine_payout(
                float(app.config["DICE_ROLL_PAYOUT"][str(guess)]),
                is_winner
            )
            net = Bet.calculate_net(wagered, payout, is_winner)

            data.append({
                "created_on": created_on,
                "updated_on": created_on,
                "user_id": user.id,
                "guess": guess,
                "dice_1": dice_1,
                "dice_2": dice_2,
                "roll": outcome,
                "wagered": wagered,
                "payout": payout,
                "net": net
            })

    return _bulk_insert(Bet, data, "bets")


@command()
@pass_context
def all(context):
    """
    Generate all data
    :param context:
    """
    context.invoke(users)
    context.invoke(invoices)
    context.invoke(bets)


cli.add_command(users)
cli.add_command(invoices)
cli.add_command(bets)
cli.add_command(all)
