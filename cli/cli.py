from os import listdir
from os.path import dirname
from os.path import join as join_path

from click import MultiCommand
from click import command


class SnakeEyesCLI(MultiCommand):
    COMMANDS_DIR = join_path(dirname(__file__), "commands")

    def list_commands(self, ctx):
        """
        Obtain a list of all available commands.

        :param ctx: Click context
        :return: List of sorted commands
        """
        return sorted(
            [
                fname[8:-3]
                for fname in listdir(self.COMMANDS_DIR)
                if fname.endswith(".py") and fname.startswith("command_")
            ]
        )

    def get_command(self, ctx, name):
        """
        Get a specific command by looking up the module.

        :param ctx: Click context
        :param name: Command name
        :return: Module's cli function
        """
        namespace = {}
        filename = join_path(self.COMMANDS_DIR, f"command_{name}.py")

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
