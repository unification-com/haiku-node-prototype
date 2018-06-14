import logging
import subprocess
import json
from itertools import product

import click
from eosapi import Client

from haiku_node.blockchain.acl import UnificationACL
from haiku_node.config.config import UnificationConfig
from haiku_node.eosio_helpers.accounts import AccountManager
from haiku_node.validation.validation import UnificationAppScValidation
from haiku_node.eosio_helpers import eosio_account

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

    apps = []

    valid_apps = eos_client.get_table_rows(
        "unif.mother", "unif.mother", "validapps", True, 0, -1,
        -1)

    for va in valid_apps['rows']:
        apps.append(eosio_account.name_to_string(int(va['acl_contract_acc'])))

    click.echo(f"{bold(user)} Permissions overview:")

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
    click.echo(f"{bold(user)} is granting {bold(requester)} "
               f"access to their data held in {bold(provider)}:")

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
    click.echo(f"{bold(user)} is revoking access from {bold(requester)} "
               f"to their data in held {bold(provider)}:")
    accounts = AccountManager()
    accounts.unlock_wallet(user, password)
    result = accounts.revoke(provider, requester, user)
    accounts.lock_wallet(user)
    if result.returncode == 0:
        click.echo(bold('Revoke succeeded'))
    else:
        click.echo(bold('Revoke failed'))


@main.command()
@click.argument('user')
@click.argument('password')
def balance(user, password):
    """
    Get UND balance for an account

    \b
    :param user: The EOS user account name.
    :param password: The EOS user account's wallet password.
    """
    accounts = AccountManager()
    accounts.unlock_wallet(user, password)
    my_balance = get_balance(user)
    accounts.lock_wallet(user)

    click.echo(bold(f'{user} Balance: {my_balance}'))


@main.command()
@click.argument('from_acc')
@click.argument('to_acc')
@click.argument('amount')
@click.argument('password')
def transfer(from_acc, to_acc, amount, password):
    """
    Quick UND transfer method.

    \b
    :param from_acc: The EOS user account name SENDING the UNDs.
    :param to_acc: The EOS user account name RECEIVING the UNDs.
    :param amount: amount to send.
    :param password: The SENDING EOS user account's wallet password.
    """
    # TODO: need to make the babel client initialised, and locked to a user

    amt = "{0:.4f}".format(round(float(amount), 4))

    click.echo(f"{bold(from_acc)} is transferring {bold(amt)} UND"
               f"to {bold(to_acc)}:")

    my_balance = get_balance(from_acc)
    click.echo(bold(f'{from_acc} Old Balance: {my_balance}'))
    their_balance = get_balance(to_acc)
    click.echo(bold(f'{to_acc} Old Balance: {their_balance}'))

    accounts = AccountManager()
    accounts.unlock_wallet(from_acc, password)

    conf = UnificationConfig()
    d = {
        'from': from_acc,
        'to': to_acc,
        'quantity': f'{amt} UND',  # TODO - need to fix precision
        'memo': 'UND transfer'
    }

    cmd = ["/opt/eosio/bin/cleos", "--url", f"http://{conf['eos_rpc_ip']}:{conf['eos_rpc_port']}",
           "--wallet-url", f"http://{conf['eos_wallet_ip']}:{conf['eos_wallet_port']}",
           'push', 'action', 'unif.token', 'transfer',  json.dumps(d), "-p", from_acc]

    ret = subprocess.run(
        cmd, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, universal_newlines=True)

    accounts.lock_wallet(from_acc)

    stripped = ret.stdout.strip()
    click.echo(bold(f'Transfer result: {stripped}'))

    my_balance = get_balance(from_acc)
    click.echo(bold(f'{from_acc} New Balance: {my_balance}'))
    their_balance = get_balance(to_acc)
    click.echo(bold(f'{to_acc} New Balance: {their_balance}'))


def get_balance(user):
    conf = UnificationConfig()
    cmd = ["/opt/eosio/bin/cleos", "--url", f"http://{conf['eos_rpc_ip']}:{conf['eos_rpc_port']}",
           "--wallet-url", f"http://{conf['eos_wallet_ip']}:{conf['eos_wallet_port']}",
           'get', 'currency', 'balance', 'unif.token', user, 'UND']

    ret = subprocess.run(
        cmd, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, universal_newlines=True)

    stripped = ret.stdout.strip()

    if len(stripped) > 0:
        my_balance = stripped
    else:
        my_balance = '0.0000 UND'

    return my_balance


if __name__ == "__main__":
    main()
