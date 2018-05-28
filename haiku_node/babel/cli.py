import logging
import os

import click

from eosapi import Client

from haiku_node.client import HaikuDataClient, Provider
from haiku_node.config.config import UnificationConfig
from haiku_node.keystore.keystore import UnificationKeystore
from haiku_node.validation.validation import UnificationAppScValidation

log = logging.getLogger(__name__)

bold = lambda s: click.style(str(s), bold=True)


@click.group()
def main():
    pass


@main.command()
@click.argument('app_name')
@click.argument('user')
@click.argument('request_hash')
def fetch(app_name, user, request_hash):
    requesting_app = os.environ['app_name']
    password = os.environ['keystore']

    provider = Provider(app_name, 'https', f'haiku-{app_name}', 8050)
    req_hash = f'request-{request_hash}'

    click.echo(f'App {requesting_app} is requesting data from {provider.name}')

    encoded_password = str.encode(password)
    keystore = UnificationKeystore(encoded_password)

    client = HaikuDataClient(keystore)
    data_path = client.make_data_request(
        requesting_app, provider, user, req_hash)
    click.echo(f'Data written to {data_path}')


@main.command()
@click.argument('app_name')
@click.argument('user')
@click.argument('request_hash')
def read(app_name, user, request_hash):
    requesting_app = os.environ['app_name']
    password = os.environ['keystore']

    provider = Provider(app_name, 'https', f'haiku-{app_name}', 8050)
    req_hash = f'request-{request_hash}'

    click.echo(f'App {requesting_app} is reading ingested data from '
               f'{provider.name}')

    encoded_password = str.encode(password)
    keystore = UnificationKeystore(encoded_password)

    client = HaikuDataClient(keystore)
    data = client.read_data_from_store(provider, req_hash)
    click.echo(data)


@main.command()
@click.argument('provider')
@click.argument('requester')
@click.argument('user')
def permissions(provider, requester, user):
    """
    Display user permissions.

    \b
    :param provider: The app name of the data provider.
    :param requester: The app name of the data requester.
    :param user: User providing or denying access.
    """
    conf = UnificationConfig()
    eos_client = Client(
        nodes=[f"http://{conf['eos_rpc_ip']}:{conf['eos_rpc_port']}"])
    v = UnificationAppScValidation(
        eos_client, provider, requester, get_perms=True)

    app_valid = v.valid_app()
    code_valid = v.valid_code()
    both_valid = v.valid()

    click.echo(f"Requesting App {requester} Valid according to MOTHER: "
               f"{bold(app_valid)}")

    click.echo(f"{requester} contract code hash valid: {bold(code_valid)}")
    click.echo(f"{requester} is considered valid: {bold(both_valid)}")

    if both_valid:
        if v.app_has_user_permission(user):
            grant = bold('GRANTED')
        else:
            grant = bold('NOT GRANTED')
        click.echo(f"{user} {grant} permission for {requester} to access data "
                   f"in {provider}")


if __name__ == "__main__":
    main()
