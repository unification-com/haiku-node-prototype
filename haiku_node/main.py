import os

import click

from cryptography.fernet import Fernet

from haiku_node.config.config import UnificationConfig
from haiku_node.keystore.keystore import UnificationKeystore
from haiku_node.rpc import app

PORT = 8050

bold = lambda s: click.style(str(s), bold=True)


@click.group()
def main():
    pass


def spawn_haiku_node(pw, config):
    encoded_password = str.encode(pw)
    ks = UnificationKeystore(encoded_password)

    setattr(app, 'keystore', ks)
    setattr(app, 'unification_config', config)
    app.run(debug=False, host="0.0.0.0", port=PORT, ssl_context='adhoc')


@main.command()
@click.argument('password', required=False)
def serve(password):
    """
    Serve the Haiku RPC service.
    """
    config = UnificationConfig()

    if not config['server_initialised']:
        click.echo(f'Server not initialized: Run {bold("haiku init")}')
    else:
        if password:
            spawn_haiku_node(password, config)
        else:
            env_password = os.environ.get('keystore')
            if not env_password:
                click.echo('Password not provided in args nor ENV var')
            else:
                spawn_haiku_node(env_password, config)


@main.command()
def init():
    """
    Initialize the Haiku Server.
    """
    config = UnificationConfig()

    if config['server_initialised']:
        click.echo(f'Server already initialized')
    else:
        pw = Fernet.generate_key()
        click.echo("Generated password:\n")
        click.echo(bold(pw.decode('utf-8')))
        click.echo("\n")
        click.echo("IMPORTANT: KEEP THIS SAFE!! YOU WILL NEED IT TO RUN THE "
                   "SERVER")
        click.echo("Run again with pw")

        config["server_initialised"] = True


if __name__ == "__main__":
    main()
