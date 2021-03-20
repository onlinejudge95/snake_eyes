import os
import subprocess

from click import argument
from click import command


@command()
@argument("path", default=os.path.join("snake_eyes", "tests"))
def cli(path):
    """
    Run tests with Pytest.

    :param path: Test path

    :return: Subprocess call result
    """
    shell_command = f"pytest {path}"
    return subprocess.call(shell_command, shell=True)
