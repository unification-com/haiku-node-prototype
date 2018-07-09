from eosapi import Client

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from haiku_node.blockchain.acl import UnificationACL
from haiku_node.blockchain.ipfs import IPFSDataStore
from haiku_node.config.config import UnificationConfig


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
