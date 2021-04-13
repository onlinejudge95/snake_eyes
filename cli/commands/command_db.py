from click import command
from click import group
from click import option
from click import pass_context
from sqlalchemy_utils import create_database
from sqlalchemy_utils import database_exists

from snake_eyes.app import create_app
from snake_eyes.extensions import db
from snake_eyes.blueprints.user.models import User


app = create_app()
db.app = app


@group()
def cli():
    """
    Run db related tasks
    """
    pass


@command()
@option(
    "--with-test-db/--no-with-test-db",
    default=False,
    help="Create a test db"
)
def init(with_test_db):
    """
    Initialize the db
    :param with_test_db: Create a test database
    """
    db.drop_all()
    db.create_all()

    if with_test_db:
        db_uri = f"{app.config['SQLALCHEMY_DATABASE_URI']}_test"

        if not database_exists(db_uri):
            create_database(db_uri)


@command()
def seed():
    """
    Seed the db with an initial user

    :return: User
    """
    if User.find_by_identity(app.config["SEED_ADMIN_EMAIL"]) is None:
        params = {
            "role": "admin",
            "email": app.config["SEED_ADMIN_EMAIL"],
            "password": app.config["SEED_ADMIN_PASSWORD"]
        }

        return User(**params).save()


@command()
@option(
    "--with-test-db/--no-with-test-db",
    default=False,
    help="Reset the test db"
)
@pass_context
def reset(ctx, with_test_db):
    """
    Initialize the db and seed as well.
    :param with_test_db: Create a test database
    """
    ctx.invoke(init, with_test_db=with_test_db)
    ctx.invoke(seed)


cli.add_command(init)
cli.add_command(seed)
cli.add_command(reset)
