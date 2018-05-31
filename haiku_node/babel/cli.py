import logging
import os

import click

from eosapi import Client

from haiku_node.client import HaikuDataClient, Provider, Unauthorized
from haiku_node.config.config import UnificationConfig
from haiku_node.eosio_helpers.accounts import AccountManager
from haiku_node.keystore.keystore import UnificationKeystore
from haiku_node.validation.validation import UnificationAppScValidation

log = logging.getLogger(__name__)

bold = lambda s: click.style(str(s), bold=True)


@click.group()
def main():
    pass


@main.command()
@click.argument('provider')
@click.argument('user')
@click.argument('request_hash')
def fetch(provider, user, request_hash):
    """
    Fetch data from an App to this App for a particular user.

    \b
    :param provider: The app name of the data provider.
    :param user: The EOS user account name to query.
    :param request_hash: The particular piece of data in concern.
    :return:
    """
    requesting_app = os.environ['app_name']
    password = os.environ['keystore']

    provider = Provider(provider, 'https', f'haiku-{provider}', 8050)
    req_hash = f'request-{request_hash}'

    click.echo(f'App {requesting_app} is requesting data from {provider.name}')

    encoded_password = str.encode(password)
    keystore = UnificationKeystore(encoded_password)

    client = HaikuDataClient(keystore)
    try:
        data_path = client.make_data_request(
            requesting_app, provider, user, req_hash)
        click.echo(f'Data written to {data_path}')
    except Unauthorized:
        click.echo(f'{user} has {bold("not authorized")} this request')


@main.command()
@click.argument('provider')
@click.argument('user')
@click.argument('request_hash')
def view(provider, user, request_hash):
    """
    Read data stored locally from an Data Provider for a particular user.

    \b
    :param provider: The app name of the data provider.
    :param user: The EOS user account name to query.
    :param request_hash: The particular piece of data in concern.
    :return:
    """
    requesting_app = os.environ['app_name']
    password = os.environ['keystore']

    provider = Provider(provider, 'https', f'haiku-{provider}', 8050)
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
    :param user: The EOS user account name to query.
    """
    conf = UnificationConfig()
    eos_client = Client(
        nodes=[f"http://{conf['eos_rpc_ip']}:{conf['eos_rpc_port']}"])
    v = UnificationAppScValidation(
        eos_client, provider, requester, get_perms=True)

    app_valid = v.valid_app()
    code_valid = v.valid_code()
    both_valid = v.valid()

    click.echo(f"The App {requester} Valid according to Unification: "
               f"{bold(app_valid)}")
    click.echo(f"The contract code of this app has a valid hash: "
               f"{bold(code_valid)}\n")

    if both_valid:
        if v.app_has_user_permission(user):
            grant = bold('GRANTED')
        else:
            grant = bold('NOT GRANTED')
        click.echo(f"{user} {grant} permission for {requester} to access data "
                   f"in {provider}")


@main.command()
@click.argument('provider')
@click.argument('requester')
@click.argument('user')
@click.argument('password')
def grant(provider, requester, user, password):
    """
    User grants data access between a provider and a requester.

    \b
    :param provider: The app name of the data provider.
    :param requester: The app name of the data requester.
    :param user: The EOS user account name that is granting access.
    :param password: The EOS user account's password.
    """
    accounts = AccountManager()
    accounts.unlock_wallet(user, password)
    result = accounts.grant(provider, requester, user)
    accounts.lock_wallet(user)
    if result.returncode == 0:
        click.echo(bold('Grant succeeded'))
    else:
        click.echo(bold('Grant failed'))


@main.command()
@click.argument('provider')
@click.argument('requester')
@click.argument('user')
@click.argument('password')
def revoke(provider, requester, user, password):
    """
    User revokes data access between a provider and a requester.

    \b
    :param provider: The app name of the data provider.
    :param requester: The app name of the data requester.
    :param user: The EOS user account name that is revoking access.
    :param password: The EOS user account's password.
    """
    accounts = AccountManager()
    accounts.unlock_wallet(user, password)
    result = accounts.revoke(provider, requester, user)
    accounts.lock_wallet(user)
    if result.returncode == 0:
        click.echo(bold('Revoke succeeded'))
    else:
        click.echo(bold('Revoke failed'))


if __name__ == "__main__":
    main()
