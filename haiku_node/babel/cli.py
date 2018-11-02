import logging
import subprocess
import json
import requests
from itertools import product

import click
from eosapi import Client

from haiku_node.blockchain_helpers.eos.eos_keys import UnifEosKey
from haiku_node.config.config import UnificationConfig
from haiku_node.blockchain.eos.uapp import UnificationUapp
from haiku_node.blockchain_helpers.eos import eosio_account
from haiku_node.blockchain_helpers.accounts import AccountManager
from haiku_node.blockchain_helpers.eos.eosio_cleos import EosioCleos
from haiku_node.encryption.jwt.jwt import UnifJWT
from haiku_node.utils.utils import (generate_nonce, generate_perm_digest_sha)
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

    for key, schema in uapp_sc.get_all_db_schemas().items():
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
        'quantity': f'{amt} UND',
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


def get_balance(user):
    """
    Get UND Balance for a user

    \b
    :param user: The EOS user account name.
    """
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


@main.command()
@click.argument('user')
@click.argument('password')
@click.argument('provider')
@click.argument('consumer')
def modify_permissions(user, password, provider, consumer, perm='active'):
    """
    Modify permissions

    \b
    :param user: The EOS user account name.
    :param password: Wallet password for user.
    :param provider: Provider EOS account name
    :param consumer: Consumer EOS account name
    :param perm: EOS Permission level to use for acquiring keys
    """

    conf = UnificationConfig()
    eos_client = Client(
        nodes=[f"http://{conf['eos_rpc_ip']}:{conf['eos_rpc_port']}"])

    uapp_sc = UnificationUapp(eos_client, provider)

    click.echo(f"{provider} has the following Schemas:\n")

    provider_schemas = uapp_sc.get_all_db_schemas().items()
    schemas_map = {}

    for key, schema in provider_schemas:
        s_id = schema['pkey']
        fields = []
        for field in schema['schema']['fields']:
            if field['name'] != 'account_name':
                fields.append(field['name'])
        schemas_map[s_id] = fields

    for key, fields in schemas_map.items():
        click.echo(f"Schema ID {key}:")
        click.echo(', '.join(fields))

    schema_id = int(input(f"Select Schema ID:"))

    schema_fields = schemas_map[schema_id]

    # ToDo - get user's current permission levels from provider/IPFS etc.
    field_perms = {}

    for f in schema_fields:
        field_perms[f] = True
        click.echo(f"{f} = True")

    perm_action = input("Type field name to toggle permission, or 's' to send: ")

    while perm_action != 's':
        if perm_action in field_perms:
            field_perms[perm_action] = not field_perms[perm_action]
        else:
            click.echo("Invalid field name")

        for n, v in field_perms.items():
            click.echo(f"{n} = {v}")

        perm_action = input("Type field name to toggle permission, or 's' to send: ")

    granted_fields = []
    for n, v in field_perms.items():
        if v:
            granted_fields.append(n)

    granted_fields_str = ",".join(granted_fields)

    click.echo(f"{user} is Requesting permission change: Granting access to {consumer} "
               f"in Provider {provider} for fields {granted_fields_str}")

    cleos = EosioCleos()
    cleos.unlock_wallet(user, password)

    pub_key = cleos.get_public_key(user, perm)

    # ToDo: find better way to get public key from EOS account
    private_key = cleos.get_private_key(user, password, pub_key)

    p_nonce = generate_nonce(16)
    perm_digest_sha = generate_perm_digest_sha(granted_fields_str, schema_id,  p_nonce, consumer)

    # sign permission changes
    eosk = UnifEosKey(private_key)
    p_sig = eosk.sign(perm_digest_sha)

    if len(private_key) > 0:
        jwt_payload = {
            'iss': user,  # RFC 7519 4.1.1
            'sub': 'perm_request',  # RFC 7519 4.1.2
            'aud': provider,  # RFC 7519 4.1.3
            'eos_perm': perm,
            'consumer': consumer,
            'schema_id': schema_id,
            'perms': granted_fields_str,
            'p_nonce': p_nonce,
            'p_sig': p_sig
        }

        cleos.lock_wallet(user)

        unif_jwt = UnifJWT()
        unif_jwt.generate(jwt_payload)
        unif_jwt.sign(private_key)

        jwt = unif_jwt.to_jwt()

        payload = {
            'jwt': jwt,
            'eos_perm': perm,
            'user': user,
            'provider': provider
        }

        base = f"https://haiku-{provider}:8050"

        r = requests.post(f"{base}/modify_permission", json=payload, verify=False)
        d = r.json()

        proc_id = d['proc_id']
        ret_app = d['app']

        if ret_app == provider and proc_id > 0:
            click.echo(f"Success. Process ID {proc_id} Queued by {ret_app}")
        else:
            click.echo("Something went wrong...")

    else:
        click.echo(bold(f'Could not get private key for {pub_key}'))


if __name__ == "__main__":
    main()
