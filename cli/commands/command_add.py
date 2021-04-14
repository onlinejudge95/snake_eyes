from datetime import datetime
from random import random

from click import command
from click import echo
from click import group
from click import pass_context
from faker import Faker

from snake_eyes.app import create_app
from snake_eyes.extensions import db
from snake_eyes.blueprints.user.models import User


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

        email = random_emails.pop()

        params = {
            "created_on": created_on,
            "updated_on": created_on,
            "role": role,
            "email": email,
            "username": username,
            "password": User.encrypt_password("password"),
            "sign_in_count": random() * 100,
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
@pass_context
def all(context):
    """
    Generate all data
    :param context:
    """
    context.invoke(users)


cli.add_command(users)
cli.add_command(all)
