import logging

import click
from eosapi import Client

from haiku_node.config.config import UnificationConfig
from haiku_node.blockchain_helpers import eosio_account
from haiku_node.blockchain_helpers.accounts import AccountManager
from haiku_node.blockchain_helpers.eosio_cleos import EosioCleos

log = logging.getLogger(__name__)

bold = lambda s: click.style(str(s), bold=True)


@click.group()
def main():
    pass


@main.command()
def validapps():
    """
    Display valid apps.

    \b
    """
    click.echo(bold("Valid apps according to MOTHER:"))

    conf = UnificationConfig()
    eos_client = Client(
        nodes=[f"http://{conf['eos_rpc_ip']}:{conf['eos_rpc_port']}"])

    valid_apps = eos_client.get_table_rows(
        "unif.mother", "unif.mother", "validapps", True, 0, -1,
        -1)

    for va in valid_apps['rows']:
        if int(va['is_valid']) == 1:
            click.echo(bold(f"{eosio_account.name_to_string(int(va['acl_contract_acc']))}"))
            click.echo(f"Schema Version: {va['schema_vers']}")
            click.echo(f"Contract Hash: {va['acl_contract_hash']}")
            click.echo(f"RPC Server: http://{va['rpc_server_ip']}:{va['rpc_server_port']}")
            click.echo("is valid: true")


@main.command()
def invalidapps():
    """
    Display invalid apps.

    \b
    """
    click.echo(bold("Invalid apps according to MOTHER:"))

    conf = UnificationConfig()
    eos_client = Client(
        nodes=[f"http://{conf['eos_rpc_ip']}:{conf['eos_rpc_port']}"])

    valid_apps = eos_client.get_table_rows(
        "unif.mother", "unif.mother", "validapps", True, 0, -1,
        -1)

    for va in valid_apps['rows']:
        if int(va['is_valid']) == 0:
            click.echo(bold(f"{eosio_account.name_to_string(int(va['acl_contract_acc']))}"))
            click.echo(f"Schema Version: {va['schema_vers']}")
            click.echo(f"Contract Hash: {va['acl_contract_hash']}")
            click.echo(f"RPC Server: http://{va['rpc_server_ip']}:{va['rpc_server_port']}")
            click.echo("is valid: false")


@main.command()
@click.argument('appname')
@click.argument('password')
def validate(appname, password):
    """
    User grants data access between a provider and a requester.

    \b
    :param appname: The app name of the data provider.
    :param password: The Mother EOS user account's password.
    """
    click.echo(f"Validating app {bold(appname)} "
               "with MOTHER:")

    cleos = EosioCleos()
    accounts = AccountManager()
    cleos.unlock_wallet('unif.mother', password)
    result = accounts.validate_with_mother(appname)
    cleos.lock_wallet('unif.mother')
    if result.returncode == 0:
        click.echo(bold('Validation succeeded'))
    else:
        click.echo(bold('Validation failed'))


@main.command()
@click.argument('appname')
@click.argument('password')
def invalidate(appname, password):
    """
    User grants data access between a provider and a requester.

    \b
    :param appname: The app name of the data provider.
    :param password: The Mother EOS user account's password.
    """
    click.echo(f"Invalidating app {bold(appname)} "
               "with MOTHER:")

    cleos = EosioCleos()
    accounts = AccountManager()
    cleos.unlock_wallet('unif.mother', password)
    result = accounts.invalidate_with_mother(appname)
    cleos.lock_wallet('unif.mother')
    if result.returncode == 0:
        click.echo(bold('Invalidation succeeded'))
    else:
        click.echo(bold('Invalidation failed'))


if __name__ == "__main__":
    main()
