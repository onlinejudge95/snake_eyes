from subprocess import call

from click import argument
from click import command
from click import group


@group()
def cli():
    """
    Run db related tasks
    """
    pass


@command()
@argument("message")
@argument("revision_id")
def migration(message, revision_id):
    shell_command = f"alembic revision --autogenerate --message '{message}' --rev-id {revision_id}"
    return call(shell_command, shell=True)


@command()
@argument("revision")
def upgrade(revision):
    shell_command = f"alembic upgrade {revision}"
    return call(shell_command, shell=True)


@command()
@argument("revision")
def downgrade(revision):
    shell_command = f"alembic downgrade {revision}"
    return call(shell_command, shell=True)


cli.add_command(migration)
cli.add_command(upgrade)
cli.add_command(downgrade)
