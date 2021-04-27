from os.path import join as join_path
from subprocess import call

from click import command
from click import group
from click import option


APP_NAME = "/snake_eyes/snake_eyes"
BABEL_I18N_PATH = join_path(APP_NAME, "translations")
MESSAGES_PATH = join_path(APP_NAME, "translations", "messages.pot")


@group()
def cli():
    """
    Perform i18n tasks
    """
    pass


@command()
def extract():
    """
    Extracts all strings into pot file
    """
    shell_command = f"pybabel extract --mapping-file babel.cfg --keyword lazy_gettext --output-file {MESSAGES_PATH} {APP_NAME}"
    return call(shell_command, shell=True)


@command()
@option("--language", default=None, help="The output language")
def init(language):
    """
    Map translations to a different language.
    """
    shell_command = f"pybabel init --input-file {MESSAGES_PATH} --output-dir {BABEL_I18N_PATH} --locale {language}"
    return call(shell_command, shell=True)


@command()
def translate():
    """
    Creates new translations
    """
    shell_command = f"pybabel compile --directory {BABEL_I18N_PATH}"
    return call(shell_command, shell=True)


@command()
def update():
    """
    Updates existing translations
    """
    shell_command = (
        f"pybabel update --input-file {MESSAGES_PATH} --output-dir {BABEL_I18N_PATH}"
    )
    return call(shell_command, shell=True)


cli.add_command(extract)
cli.add_command(init)
cli.add_command(translate)
cli.add_command(update)
