import subprocess

from click import argument
from click import command


@command()
@argument("path", default="/snake_eyes")
def cli(path):
    """
    Run a test coverage report.

    :param path: Test coverage path

    :return: Subprocess call result
    """
    shell_command = f"pytest --cov-branch --cov /snake_eyes/snake_eyes --cov-report term-missing {path}"
    return subprocess.call(shell_command, shell=True)
