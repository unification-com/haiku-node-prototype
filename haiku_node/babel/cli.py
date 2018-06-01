import logging
from itertools import product

import click
from eosapi import Client

from haiku_node.blockchain.acl import UnificationACL
from haiku_node.config.config import UnificationConfig
from haiku_node.eosio_helpers.accounts import AccountManager
from haiku_node.validation.validation import UnificationAppScValidation

log = logging.getLogger(__name__)

bold = lambda s: click.style(str(s), bold=True)


@click.group()
def main():
    pass


@main.command()
@click.argument('user')
def permissions(user):
    """
    Display user permissions.

    \b
    :param user: The EOS user account name to query.
    """
    conf = UnificationConfig()
    eos_client = Client(
        nodes=[f"http://{conf['eos_rpc_ip']}:{conf['eos_rpc_port']}"])

    apps = conf.registered_apps
    for requester, provider in product(apps, apps):
        if requester == provider:
            continue
        v = UnificationAppScValidation(
            eos_client, provider, requester, get_perms=True)
        if v.app_has_user_permission(user):
            grant = bold('GRANTED')
        else:
            grant = bold('NOT GRANTED')
        click.echo(f"{requester} {grant} to read from {provider}")


@main.command()
@click.argument('app_name')
def sources(app_name):
    """
    Obtain data source information about an App.

    \b
    :param app_name: The EOS app account name to query.
    """
    conf = UnificationConfig()
    eos_client = Client(
        nodes=[f"http://{conf['eos_rpc_ip']}:{conf['eos_rpc_port']}"])

    acl = UnificationACL(eos_client, app_name)
    datasources = acl.get_data_sources()

    click.echo(f"{app_name} has the following datasources:\n")

    schemas = {}
    for k, d in acl.get_db_schemas().items():
        schemas[d['schema_name_str']] = d['schema']

    for k, d in datasources.items():
        click.echo(f"A {bold(d['source_type'])} source from "
                   f"{d['source_name_str']}")
        if d['source_type'] == 'database':
            click.echo(
                f"The schema for {d['source_name_str']} is "
                f"{schemas[d['source_name_str']]}")


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
