from binascii import b2a_hex
from os import urandom

from click import argument
from click import command
from click import echo


@command()
@argument("length", default=128)
def cli(length):
    """
    Generate a random secret token

    :param length: Number of bytes to use
    :return: str
    """
    return echo(b2a_hex(urandom(length)))
