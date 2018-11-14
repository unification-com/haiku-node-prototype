import json
import requests
import subprocess

import click

from haiku_node.babel.babel_db import (BabelDatabase, default_db as default_babel_db)
from haiku_node.blockchain.eos.mother import UnificationMother
from haiku_node.blockchain.eos.uapp import UnificationUapp
from haiku_node.config.config import UnificationConfig
from haiku_node.client import Provider
from haiku_node.encryption.merkle.merkle_tree import MerkleTree
from haiku_node.network.eos import get_eos_rpc_client, get_cleos, get_ipfs_client
from haiku_node.permissions.utils import generate_payload

bold = lambda s: click.style(str(s), bold=True)


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

    # ToDo: find better way to get public key from EOS account
    pub_key = cleos.get_public_key(user, perm)

    cleos.unlock_wallet(user, password)
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
