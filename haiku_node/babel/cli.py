import logging
import subprocess
import json
from itertools import product

import click
from eosapi import Client

from haiku_node.config.config import UnificationConfig
from haiku_node.blockchain.uapp import UnificationUapp
from haiku_node.blockchain_helpers import eosio_account
from haiku_node.blockchain_helpers.accounts import AccountManager
from haiku_node.blockchain_helpers.eosio_cleos import EosioCleos
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
def schemas(app_name):
    """
    Obtain data source information about an App.

    \b
    :param app_name: The EOS app account name to query.
    """
    conf = UnificationConfig()
    eos_client = Client(
        nodes=[f"http://{conf['eos_rpc_ip']}:{conf['eos_rpc_port']}"])

    uapp_sc = UnificationUapp(eos_client, app_name)

    click.echo(f"{app_name} has the following Schemas:\n")

    for schema in uapp_sc.get_all_db_schemas():
        click.echo(f"Schema ID {schema['pkey']}:")
        click.echo(schema['schema'])


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

    cleos = EosioCleos()
    accounts = AccountManager()
    cleos.unlock_wallet(user, password)
    result = accounts.grant(provider, requester, user)
    cleos.lock_wallet(user)
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
    cleos = EosioCleos()
    accounts = AccountManager()
    cleos.unlock_wallet(user, password)
    result = accounts.revoke(provider, requester, user)
    cleos.lock_wallet(user)
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
    cleos = EosioCleos()
    cleos.unlock_wallet(user, password)
    my_balance = get_balance(user)
    cleos.lock_wallet(user)

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

    cleos = EosioCleos()
    cleos.unlock_wallet(from_acc, password)

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

    cleos.lock_wallet(from_acc)

    stripped = ret.stdout.strip()
    click.echo(bold(f'Transfer result: {stripped}'))

    my_balance = get_balance(from_acc)
    click.echo(bold(f'{from_acc} New Balance: {my_balance}'))
    their_balance = get_balance(to_acc)
    click.echo(bold(f'{to_acc} New Balance: {their_balance}'))


@main.command()
@click.argument('consumer')
@click.argument('password')
def store(consumer, password):
    """
        Display a list of valid apps, and their schemas.
        Allow option to initiate a data transfer
    """
    click.echo(bold("UApp Store"))

    conf = UnificationConfig()
    eos_client = Client(
        nodes=[f"http://{conf['eos_rpc_ip']}:{conf['eos_rpc_port']}"])

    valid_apps = eos_client.get_table_rows(
        "unif.mother", "unif.mother", "validapps", True, 0, -1,
        -1)

    uapp_store = {}
    store_key = 1

    for va in valid_apps['rows']:
        data_provider = eosio_account.name_to_string(int(va['acl_contract_acc']))
        if int(va['is_valid']) == 1 and data_provider != consumer:
            uapp_sc = UnificationUapp(eos_client, data_provider)
            db_schemas = uapp_sc.get_all_db_schemas()
            click.echo(bold(f"Data Provider: {data_provider}"))
            for pkey, db_schema in db_schemas.items():
                schema = db_schema['schema']
                click.echo(bold(f"Option {store_key}:"))
                click.echo("    Data available:")
                for field in schema['fields']:
                    click.echo(f"        {field['name']}, {field['type']}")
                click.echo(f"    Scheduled Price: {db_schema['price_sched']} UND")
                click.echo(f"    Ad-hoc Price: {db_schema['price_adhoc']} UND")
                click.echo("    Availability: daily")

                d = {
                    'provider': data_provider,
                    'pkey': pkey
                }
                uapp_store[store_key] = d
                store_key += 1

    request_id = int(input(f"Select option 1 - {(store_key - 1)} to initialise a data request, or '0' to exit:"))
    if request_id > 0 and request_id <= store_key:
        data_request = uapp_store[request_id]
        cleos = EosioCleos()
        cleos.unlock_wallet(consumer, password)

        # Todo: stub for sending request info to Haiku Client
        click.echo("Selected:")
        click.echo(data_request)

        cleos.lock_wallet(consumer)

    else:
        click.echo("Exit Uapp Store")


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
