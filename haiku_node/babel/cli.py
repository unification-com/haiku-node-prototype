import logging
import subprocess
import json
import requests
import urllib3

import click

from haiku_node.babel.babel_db import (BabelDatabase, default_db as default_babel_db)
from haiku_node.blockchain.eos.mother import UnificationMother
from haiku_node.client import Provider
from haiku_node.config.config import UnificationConfig
from haiku_node.blockchain.eos.uapp import UnificationUapp
from haiku_node.blockchain_helpers.eos import eosio_account
from haiku_node.blockchain_helpers.eos.eosio_cleos import EosioCleos
from haiku_node.encryption.merkle.merkle_tree import MerkleTree
from haiku_node.network.eos import get_eos_rpc_client, get_cleos, get_ipfs_client
from haiku_node.permissions.utils import generate_payload

log = logging.getLogger(__name__)

bold = lambda s: click.style(str(s), bold=True)

ZERO_MASK = '0000000000000000000000000000000000000000000000'

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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
    eos_rpc_client = get_eos_rpc_client()
    ipfs_client = get_ipfs_client()

    apps = []

    valid_apps = eos_rpc_client.get_table_rows(
        "unif.mother", "unif.mother", "validapps", True, 0, -1,
        -1)

    for va in valid_apps['rows']:
        apps.append(eosio_account.name_to_string(int(va['acl_contract_acc'])))

    click.echo(f"{bold(user)} Permissions overview:")

    # ToDo: get permissions from SC/IPFS
    for provider in apps:
        click.echo(f'Provider: {bold(provider)}')
        for consumer in apps:
            if consumer != provider:
                click.echo(f'  Consumer: {bold(consumer)}')
                uapp_sc = UnificationUapp(eos_rpc_client, provider)
                ipfs_hash, merkle_root = uapp_sc.get_ipfs_perms_for_req_app(consumer)
                if ipfs_hash is not None and ipfs_hash != ZERO_MASK:
                    permissions_str = ipfs_client.get_json(ipfs_hash)
                    permissions_json = json.loads(permissions_str)
                    user_perms = permissions_json[user]
                    for schema_id, permissions in user_perms.items():
                        click.echo(f'    Schema ID: {schema_id}')
                        if permissions['perms'] == '':
                            click.echo('      Granted: False')
                        else:
                            click.echo('      Granted: True')
                            click.echo(f"      Fields: {permissions['perms']}")
                else:
                    click.echo('Nothing set')


@main.command()
@click.argument('app_name')
def schemas(app_name):
    """
    Obtain data source information about an App.

    \b
    :param app_name: The EOS app account name to query.
    """
    eos_client = get_eos_rpc_client()

    uapp_sc = UnificationUapp(eos_client, app_name)

    click.echo(f"{app_name} has the following Schemas:\n")

    for key, schema in uapp_sc.get_all_db_schemas().items():
        click.echo(f"Schema ID {schema['pkey']}:")
        click.echo(schema['schema'])


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
           'push', 'action', 'unif.token', 'transfer', json.dumps(d), "-p", from_acc]

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


def get_schemas(provider):
    eos_client = get_eos_rpc_client()

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

    return schemas_map


def post_permissions(user, password, perm, granted_fields_str: str,
                     schema_id: int, provider, consumer):

    babel_db = BabelDatabase(default_babel_db(user))

    cleos = get_cleos()

    cleos.unlock_wallet(user, password)

    pub_key = cleos.get_public_key(user, perm)

    # ToDo: find better way to get public key from EOS account
    private_key = cleos.get_private_key(user, password, pub_key)
    cleos.lock_wallet(user)

    if len(private_key) < 0:
        click.echo(bold(f'Could not get private key for {pub_key}'))
        return

    payload, p_nonce, p_sig = generate_payload(
        user, private_key, provider, consumer, granted_fields_str, perm,
        schema_id)

    request_id = babel_db.add_change_request(user, provider, consumer, schema_id,
                                             granted_fields_str, p_nonce, p_sig, pub_key)

    url = get_rpc_url(provider, 'modify_permission')

    r = requests.post(url, json=payload, verify=False)

    d = r.json()

    if r.status_code != 200:
        raise Exception(d['message'])

    proc_id = d['proc_id']
    ret_app = d['app']

    if ret_app == provider and proc_id > 0:
        babel_db.update_provider_process_id(request_id, proc_id)
        click.echo(f"Success. Process ID {proc_id} Queued by {ret_app}")
        click.echo(f'Request ID: {request_id}')
        click.echo(f'Check status, run:')
        click.echo(f'babel check_change_request {user} {request_id}')

    else:
        click.echo("Something went wrong...")


def get_proof_chain(user, provider, schema_id='0', consumer=None, ipfs_hash=None):
    payload = {
        'consumer': consumer,
        'user': user,
        'ipfs_hash': ipfs_hash,
        'schema_id': schema_id
    }

    url = get_rpc_url(provider, 'get_proof')

    r = requests.post(url, json=payload, verify=False)

    d = r.json()

    if r.status_code != 200:
        return None
    else:
        # ToDo: receive as JWT and verify
        return d['proof']


def generate_leaf_from_ipfs(user, schema_id, ipfs_hash):
    ipfs_client = get_ipfs_client()
    permissions_str = ipfs_client.get_json(ipfs_hash)

    permissions_json = json.loads(permissions_str)

    return json.dumps(permissions_json[user][schema_id])


def verify_proof(merkle_root, proof_chain, permission_obj):

    requested_leaf = json.dumps(permission_obj)

    verify_tree = MerkleTree()
    return verify_tree.verify_leaf(requested_leaf, merkle_root,
                                   proof_chain, is_hashed=False)


def get_rpc_url(provider, endpoint):
    mother = UnificationMother(get_eos_rpc_client(), provider, get_cleos())
    provider_obj = Provider(provider, 'https', mother)
    return f"{provider_obj.base_url()}/{endpoint}"


def get_current_ipfs_merkle(provider, consumer):
    uapp_sc = UnificationUapp(get_eos_rpc_client(), provider)
    ipfs_hash, merkle_root = uapp_sc.get_ipfs_perms_for_req_app(consumer)
    return ipfs_hash, merkle_root


def get_ipfs_merkle_from_proof_tx(proof_tx, provider, consumer):
    ipfs_hash = None
    merkle_root = None

    eos_cleos = get_cleos()

    transaction_data = eos_cleos.get_tx(proof_tx)

    if transaction_data is None:
        click.echo(f'Tx {proof_tx} not found on blockchain')
        return

    tx_json = json.loads(transaction_data)

    tx_actions = tx_json["trx"]["trx"]["actions"]

    for action in tx_actions:
        if (
                action['account'] == provider
                and action['name'] == 'updateperm'
                and action['data']['consumer_id'] == consumer
        ):
            click.echo(f'Found change request process')
            ipfs_hash = action['data']['ipfs_hash']
            merkle_root = action['data']['merkle_root']

    return ipfs_hash, merkle_root


def generate_leaf_to_prove(data, user):
    leaf_to_prove = {
        "perms": data['perms'],
        "p_nonce": data['p_nonce'],
        "p_sig": data['p_sig'],
        "pub_key": data['pub_key'],
        "schema_id": data['schema_id'],
        "consumer": data['consumer_account'],
        "user": user
    }

    return leaf_to_prove


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
    :param provider: Provider EOS account name.
    :param consumer: Consumer EOS account name.
    :param perm: EOS Permission level to use for acquiring keys.
    """

    schemas_map = get_schemas(provider)

    schema_id = int(input(f"Select Schema ID:"))

    schema_fields = schemas_map[schema_id]

    # ToDo - get user's current permission levels from provider/IPFS etc.
    field_perms = {}

    for f in schema_fields:
        field_perms[f] = True
        click.echo(f"{f} = True")

    perm_action = input(
        "Type field name to toggle permission, or 's' to send: ")

    while perm_action != 's':
        if perm_action in field_perms:
            field_perms[perm_action] = not field_perms[perm_action]
        else:
            click.echo("Invalid field name")

        for n, v in field_perms.items():
            click.echo(f"{n} = {v}")

        perm_action = input(
            "Type field name to toggle permission, or 's' to send: ")

    granted_fields = []
    for n, v in field_perms.items():
        if v:
            granted_fields.append(n)

    granted_fields_str = ",".join(granted_fields)

    click.echo(f"{user} is Requesting permission change: Granting access to "
               f"{consumer} in Provider {provider} for fields {granted_fields}")

    post_permissions(
        user, password, perm, granted_fields_str, schema_id, provider, consumer)


@main.command()
@click.argument('user')
@click.argument('password')
@click.argument('provider')
@click.argument('consumer')
@click.argument('schema_id')
@click.option('-f', '--fields', 'granted_fields', required=False, default='')
def modify_permissions_direct(
        user, password, provider, consumer, schema_id, granted_fields):
    """
    Modify permissions

    \b
    :param user: The EOS user account name.
    :param password: Wallet password for user.
    :param provider: Provider EOS account name.
    :param consumer: Consumer EOS account name.
    :param schema_id: The ID of the schema.
    :param granted_fields: Comma separated list of granted fields.
    """
    int(schema_id)

    if not granted_fields:
        click.echo(f"{user} is Requesting permission change: Revoking access to "
                   f"{consumer} in Provider {provider} for Schema {schema_id}")
    else:
        click.echo(f"{user} is Requesting permission change: Granting access to "
                   f"{consumer} in Provider {provider} for fields {granted_fields}"
                   f"in Schema {schema_id}")

    perm = 'active'
    post_permissions(
        user, password, perm, granted_fields, schema_id, provider, consumer)


@main.command()
@click.argument('user')
@click.argument('provider')
@click.argument('consumer')
@click.argument('schema_id')
def prove_permission(user, provider, consumer, schema_id):
    """
    Verify a user's current permission state on the blockchain
    :param user: End User's EOS account name
    :param provider: Provider's EOS account name
    :param consumer: Consumer's EOS account name
    :param schema_id: Schema ID to check
    """

    ipfs_hash, merkle_root = get_current_ipfs_merkle(provider, consumer)

    proof_chain = get_proof_chain(user, provider, schema_id=schema_id, consumer=consumer)

    if proof_chain is None:
        click.echo('Proof chain not found')
        return

    click.echo(f'IPFS Hash from {provider} SC: {ipfs_hash}')
    click.echo(f'Merkle Root from {provider} SC: {merkle_root}')
    click.echo(f'Proof Chain from {provider}: {proof_chain}')

    leaf_to_prove = generate_leaf_from_ipfs(user, schema_id, ipfs_hash)

    is_good = verify_proof(merkle_root, proof_chain, leaf_to_prove)

    click.echo(bold(f'Permissions are valid: {is_good}'))


@main.command()
@click.argument('user')
@click.argument('request_id')
def check_change_request(user, request_id):
    """
    Check state of a permission change request, and verify it has been honoured
    :param user: End User's EOS account name
    :param request_id: Request ID from user's BABEL DB
    """

    babel_db = BabelDatabase(default_babel_db(user))
    request_data = babel_db.get_request_by_id(request_id, user)

    if request_data is None:
        click.echo(f'Request ID {request_id} for {user} not found')
        return

    provider = request_data['provider_account']
    proc_id = request_data['provider_process_id']
    consumer = request_data['consumer_account']
    schema_id = request_data['schema_id']

    payload = {
        'user': user,
        'proc_id': proc_id
    }

    url = get_rpc_url(provider, 'get_proof_tx')

    r = requests.post(url, json=payload, verify=False)

    d = r.json()

    if r.status_code != 200:
        raise Exception(d['message'])

    if not d['found']:
        click.echo(f'Permission change request ID {proc_id} for User {user}, '
                   f'Provider {provider}, Consumer {consumer}, '
                   f'Schema ID {schema_id} not found')
        return

    if not d['processed']:
        click.echo(f'Permission change request ID {proc_id} '
                   f'has not been processed yet')
        return

    proof_tx = d['proof_tx']
    babel_db.update_processed(request_id, proof_tx)

    click.echo(f'Request processed in blockchain Tx ID {proof_tx}. Checking:')

    tx_ipfs_hash, tx_merkle_root = get_ipfs_merkle_from_proof_tx(proof_tx,
                                                                 provider, consumer)

    click.echo(f'IPFS Hash at time of change request: {tx_ipfs_hash}')
    click.echo(f'Merkle Root at time of change request: {tx_merkle_root}')

    tx_proof_chain = get_proof_chain(user, provider, schema_id=schema_id,
                                     ipfs_hash=tx_ipfs_hash)

    leaf_to_prove = generate_leaf_to_prove(request_data, user)

    if not request_data['perms']:
        feedback = f'revoking access to Schema {schema_id}'
    else:
        feedback = f"granting access to fields {request_data['perms']} in Schema {schema_id}"

    click.echo(f"Verifying {feedback} was processed by "
               f'Provider {provider} for Consumer {consumer}...')

    tx_is_good = verify_proof(tx_merkle_root, tx_proof_chain, leaf_to_prove)
    click.echo(bold(f'Tx proof verified: {tx_is_good}'))

    current_ipfs_hash, current_merkle_root = get_current_ipfs_merkle(provider, consumer)

    current_proof_chain = get_proof_chain(user, provider, schema_id=schema_id,
                                          ipfs_hash=current_ipfs_hash)

    current_is_good = verify_proof(current_merkle_root,
                                   current_proof_chain, leaf_to_prove)
    click.echo(f'Current IPFS Hash: {current_ipfs_hash}')
    click.echo(f'Current Merkle Root: {current_merkle_root}')

    click.echo(f"Verifying {feedback} is currently honoured by "
               f'Provider {provider} for Consumer {consumer}...')

    click.echo(bold(f'Current proof verified: {current_is_good}'))


if __name__ == "__main__":
    main()
