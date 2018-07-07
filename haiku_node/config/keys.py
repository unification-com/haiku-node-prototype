import json
import os

from pathlib import Path

from eosapi import Client

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from haiku_node.blockchain.acl import UnificationACL
from haiku_node.blockchain.ipfs import IPFSDataStore
from haiku_node.config.config import UnificationConfig
from haiku_node.keystore.keystore import UnificationKeystore


def password_for_app(app_name):
    """
    The key stores currently do not contain the public keys of the peer apps
    """
    current_directory = Path(os.path.abspath(__file__))
    par = current_directory.parent.parent.parent
    config = par / Path('test/data/demo_config.json')

    contents = config.read_text()
    d = json.loads(contents)["system"]

    return d[app_name]['password']


def get_public_key(app_name):
    config = UnificationConfig()
    eos_client = Client(
        nodes=[f"http://{config['eos_rpc_ip']}:{config['eos_rpc_port']}"])
    u_acl = UnificationACL(eos_client, app_name)
    public_key_hash = u_acl.get_public_key_hash(app_name)

    store = IPFSDataStore()
    public_key = store.cat_file(public_key_hash)

    return serialization.load_pem_public_key(
        public_key,
        backend=default_backend())


def get_private_key(app_name):
    encoded_password = str.encode(password_for_app(app_name))
    ks = UnificationKeystore(encoded_password, app_name=app_name)
    return ks.get_rpc_auth_private_key()
