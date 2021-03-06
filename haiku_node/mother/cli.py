import json
import logging
import datetime

import click

from haiku_node.blockchain_helpers.eos import eosio_account
from haiku_node.blockchain_helpers.accounts import AccountManager
from haiku_node.blockchain_helpers.eos.eosio_cleos import EosioCleos
from haiku_node.network.eos import get_eos_rpc_client, get_ipfs_client

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
    eos_client = get_eos_rpc_client()
    ipfs_client = get_ipfs_client()

    valid_apps = eos_client.get_table_rows(
        "unif.mother", "unif.mother", "validapps", True, 0, -1,
        -1)

    for va in valid_apps['rows']:
        if int(va['is_valid']) == 1:
            ipfs_hash = va['ipfs_hash']
            uapp_json_str = ipfs_client.get_json(ipfs_hash)
            uapp_json = json.loads(uapp_json_str)
            uapp_data = uapp_json['data']
            mother_sig = uapp_json['sig']
            added = datetime.datetime.utcfromtimestamp(uapp_data['time_added'])

            acc_name = eosio_account.name_to_string(
                int(va['uapp_contract_acc']))
            click.echo(f"{bold(acc_name)}: {bold(uapp_data['name'])}")
            click.echo(f"{uapp_data['description']}")
            click.echo(f"{uapp_data['website']}")
            click.echo(f"Contract Hash: {uapp_data['uapp_contract_hash']}")
            click.echo(f"RPC Server: "
                       f"http://{uapp_data['rpc_server_ip']}:"
                       f"{uapp_data['rpc_server_port']}")
            click.echo(f"UApp Registered: {added}")
            click.echo(f"MOTHER Signature: {mother_sig}")
            click.echo("is valid: true")
            click.echo("------------------------")


@main.command()
def invalidapps():
    """
    Display invalid apps.

    \b
    """
    click.echo(bold("Invalid apps according to MOTHER:"))

    eos_client = get_eos_rpc_client()
    ipfs_client = get_ipfs_client()

    valid_apps = eos_client.get_table_rows(
        "unif.mother", "unif.mother", "validapps", True, 0, -1,
        -1)

    for va in valid_apps['rows']:
        if int(va['is_valid']) == 0:
            ipfs_hash = va['ipfs_hash']
            uapp_json_str = ipfs_client.get_json(ipfs_hash)
            uapp_json = json.loads(uapp_json_str)
            uapp_data = uapp_json['data']
            mother_sig = uapp_json['sig']

            acc_name = eosio_account.name_to_string(
                int(va['uapp_contract_acc']))
            click.echo(f"{bold(acc_name)}: {bold(uapp_data['name'])}")
            click.echo(f"{bold(uapp_data['name'])}")
            click.echo(f"{uapp_data['description']}")
            click.echo(f"{uapp_data['website']}")
            click.echo(f"Contract Hash: {uapp_data['uapp_contract_hash']}")
            click.echo(f"RPC Server: "
                       f"http://{uapp_data['rpc_server_ip']}:"
                       f"{uapp_data['rpc_server_port']}")
            click.echo(f"UApp Registered: {added}")
            click.echo(f"MOTHER Signature: {mother_sig}")
            click.echo("is valid: false")
            click.echo("------------------------")


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


@main.command()
@click.argument('acc_name')
def get_actions(acc_name):
    """
    Get transaction history for an account
     \b
    :param acc_name: EOS Account name for which to list transactions
    """
    cleos = EosioCleos()
    result = cleos.get_actions(acc_name)
    click.echo(result.stdout)
    click.echo(result.stderr)


@main.command()
@click.argument('tx')
def get_tx(tx):
    """
    Get transaction details for given Tx ID
     \b
    :param tx: Tx ID
    """
    cleos = EosioCleos()
    result = cleos.get_tx(tx)
    click.echo(result.stdout)
    click.echo(result.stderr)


if __name__ == "__main__":
    main()
