import subprocess

from click import argument
from click import command
from click import option


@command()
@option("--skip-init/--no-skip-init", default=True, help="Skip __init__.py files?")
@argument("path", default="/snake_eyes")
def cli(skip_init, path):
    """
    Run linting with flake8.

    :param skip_init: Skip checking __init__.py files

    :param path: Test coverage path

    :return: Subprocess call result
    """
    flag = ",__init__.py" if skip_init else ""
    shell_command = f"flake8 --exclude env{flag} {path}"
    return subprocess.call(shell_command, shell=True)
