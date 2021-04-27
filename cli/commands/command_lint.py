from subprocess import call

from click import argument
from click import command
from click import group
from click import option


@group()
def cli():
    """
    Run linting related tasks
    """
    pass


@command()
@option("--skip-init/--no-skip-init", default=True, help="Skip __init__.py files?")
@argument("path", default="/snake_eyes")
def flake8(skip_init, path):
    """
    Run linting with flake8.

    :param skip_init: Skip checking __init__.py files

    :param path: Test coverage path

    :return: Subprocess call result
    """
    flag = ",__init__.py" if skip_init else ""
    shell_command = (
        f"flake8 --max-line-length 88 --exclude instance*,venv,migrations{flag} {path}"
    )
    return call(shell_command, shell=True)


@command()
@option("--check-only/--no-check-only", default=False, help="Only check")
@argument("path", default="/snake_eyes")
def isort(check_only, path):
    """
    Run linting with isort.

    :param path: path for sorting imports

    :return: Subprocess call result
    """
    flag = "--check-only" if check_only else ""
    shell_command = (
        "isort --atomic --force-single-line-imports"
        "--lines-after-imports 2 --lines-between-types 1 --line-length 79"
        f"--profile black --skip migrations --skip venv {flag} {path}"
    )
    return call(shell_command, shell=True)


@command()
@option("--check-only/--no-check-only", default=False, help="Only check")
@argument("path", default="/snake_eyes")
def black(check_only, path):
    """
    Run formatting with black.

    :param path: path for sorting imports

    :return: Subprocess call result
    """
    flag = "--check" if check_only else ""
    shell_command = f"black --target-version py37 {flag} {path}"
    return call(shell_command, shell=True)


cli.add_command(flake8)
cli.add_command(isort)
cli.add_command(black)
