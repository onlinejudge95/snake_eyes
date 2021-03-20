import os

from click import MultiCommand
from click import command


class SnakeEyesCLI(MultiCommand):
    COMMANDS_DIR = os.path.join(os.path.dirname(__file__), "commands")
    COMMAND_PREFIX = "command_"

    def list_commands(self, ctx):
        """
        Obtain a list of all available commands.

        :param ctx: Click context
        :return: List of sorted commands
        """
        return sorted([filename[8:-3] for filename in os.listdir(self.COMMANDS_DIR) if filename.endswith('.py') and filename.startswith(self.COMMAND_PREFIX)])

    def get_command(self, ctx, name):
        """
        Get a specific command by looking up the module.

        :param ctx: Click context
        :param name: Command name
        :return: Module's cli function
        """
        namespace = {}
        filename = os.path.join(self.COMMANDS_DIR, f"{self.COMMAND_PREFIX}{name}.py")

        with open(filename, "r") as fp:
            code = compile(fp.read(), filename, "exec")

        eval(code, namespace, namespace)

        return namespace["cli"]


@command(cls=SnakeEyesCLI)
def cli():
    """
    Custom CLI entrypoint
    """
    pass
