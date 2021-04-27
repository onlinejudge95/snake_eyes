from click import command
from click import echo

from snake_eyes.app import create_app


app = create_app()


@command()
def cli():
    """
    List all available routes
    """
    output = {
        rule.endpoint: {"path": rule.rule, "methods": f"({','.join(rule.methods)})"}
        for rule in app.url_map.iter_rules()
    }

    endpoint_padding = max(len(endpoint) for endpoint in output.keys()) + 2

    for key in sorted(output):
        if "debugtoolbar" not in key and "debug_toolbar" not in key:
            echo(f"{key : >{endpoint_padding}}: {output[key]}")
