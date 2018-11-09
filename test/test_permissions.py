import logging
import tempfile
from pathlib import Path

from unittest.mock import patch, MagicMock

from create_perm_batch_dbs import _create_perm_batch_db

from haiku_node.babel.cli import generate_payload
from haiku_node.encryption.jwt.jwt import UnifJWT
from haiku_node.encryption.merkle.merkle_tree import sha256
from haiku_node.permissions.permission_batcher import PermissionBatcher
from haiku_node.permissions.permissions import ZERO_MASK

log = logging.getLogger(__name__)


class MockIPFSDataStore:
    d = {}

    def add_json(self, json_str):
        sha = sha256(json_str)
        self.d[sha] = json_str

    def get_json(self, json_hash):
        return self.d[json_hash]

    def add_file(self):
        raise NotImplemented('Consider dropping in the original interface')

    def cat_file(self):
        raise NotImplemented('Consider dropping in the original interface')


class MockUApp:

    def get_ipfs_perms_for_req_app(self, consumer):
        return (ZERO_MASK, 0)

    def update_userperms(self, consumer, new_ipfs_hash, new_merkle_root):
        return 1


@patch('haiku_node.permissions.permission_batcher.get_ipfs_client',
       return_value=MockIPFSDataStore())
@patch('haiku_node.permissions.permission_batcher.get_self_uapp',
       return_value=MockUApp())
def test_perm_batches(get_ipfs_client, get_self_uapp):
    f = tempfile.NamedTemporaryFile(mode='w', delete=False)
    log.info(f"Writing to {f.name}")

    _create_perm_batch_db(f)
    batcher = PermissionBatcher(f)

    add_to_queue(batcher, 'DataBlob')
    add_to_queue(batcher, 'BlobSize')

    batcher.process_batch_queue()


def add_to_queue(batcher, granted_fields_str):
    private_key = '5JcVWg7GsNWoaUs6pso3RaE5oe1HQCRt87qmPCU7sLS3EiaT2gZ'
    public_key = 'EOS8RuGsSmG54KxQh8nrH6jcp2AVjsNboVpofBuPwF8odjNXXW4Uk'
    user = 'user1'
    schema_id = 0
    consumer = 'app1'
    provider = 'app2'
    perm = 'active'

    # Pack
    d = generate_payload(
        user, private_key, provider, consumer, granted_fields_str, perm,
        schema_id)

    # And unpack
    jwt = d['jwt']
    unif_jwt = UnifJWT(jwt, public_key)
    issuer = unif_jwt.get_issuer()
    payload = unif_jwt.get_payload()

    rowid = batcher.add_to_queue(issuer,
                                 payload['consumer'],
                                 payload['schema_id'],
                                 payload['perms'],
                                 payload['p_nonce'],
                                 payload['p_sig'],
                                 public_key)
