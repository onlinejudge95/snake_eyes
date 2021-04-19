from os.path import join as join_path
from subprocess import call

from click import argument
from click import command


@command()
@argument("path", default=join_path("snake_eyes", "tests"))
def cli(path):
    """
    Run tests with Pytest.

    :param path: Test path

    :return: Subprocess call result
    """
    shell_command = f"pytest --verbose {path}"
    return call(shell_command, shell=True)
