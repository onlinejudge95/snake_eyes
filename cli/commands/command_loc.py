from subprocess import check_output

from click import command
from click import echo


def count_loc(file_type, comment_pattern):
    """
    Count LOC for a given file type excluding the comments
    """
    find_command = f"find . -name '*.{file_type}' -print0"
    sed_command = f"sed '/^\s*{comment_pattern}/d;/^\s*$/d'"
    command = f"{find_command} | xargs -0 {sed_command} | wc -l"
    return check_output(command, shell=True).decode("utf-8").replace("\n", "")


@command()
def cli():
    """
    Count lines of code in this project.
    For python files it includes all the py files from workspace root
    """
    file_types = (
        ["Python", "py", "#"],
        ["HTML", "html", "<!--"],
        ["CSS", "css", "\/\*"],
        ["JS", "js", "\/\/"],
    )

    echo("Lines of code\n------------------")

    for file_type in file_types:
        echo(f"{file_type[0]}: {count_loc(file_type[1], file_type[2])}")
