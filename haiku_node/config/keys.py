from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from haiku_node.blockchain.eos.uapp import UnificationUapp
from haiku_node.network.eos import get_eos_rpc_client, get_ipfs_client


def get_public_key(app_name):
    eos_client = get_eos_rpc_client()
    uapp_sc = UnificationUapp(eos_client, app_name)
    public_key_hash = uapp_sc.get_public_key_hash(app_name)

    store = get_ipfs_client()
    public_key = store.cat_file(public_key_hash)

    return serialization.load_pem_public_key(
        public_key,
        backend=default_backend())
