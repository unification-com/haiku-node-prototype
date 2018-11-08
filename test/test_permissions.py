import logging
import tempfile

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


def mock_get_self_uapp():
    m = MagicMock()
    m.get_ipfs_perms_for_req_app.return_value = (ZERO_MASK, 0)
    m.update_userperms.return_value = 1
    return m


@patch('haiku_node.permissions.permission_batcher.get_ipfs_client',
       return_value=MockIPFSDataStore())
@patch('haiku_node.permissions.permission_batcher.get_self_uapp',
       return_value=mock_get_self_uapp())
def test_perm_batches(get_ipfs_client, get_self_uapp):
    f = tempfile.NamedTemporaryFile(mode='w', delete=False)
    log.info(f"Writing to {f.name}")

    _create_perm_batch_db(f.name)

    private_key = '5JcVWg7GsNWoaUs6pso3RaE5oe1HQCRt87qmPCU7sLS3EiaT2gZ'
    public_key = 'EOS8RuGsSmG54KxQh8nrH6jcp2AVjsNboVpofBuPwF8odjNXXW4Uk'

    user = 'user1'
    granted_fields_str = 'DataBlob'
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

    batcher = PermissionBatcher(f.name)
    rowid = batcher.add_to_queue(issuer,
                                 payload['consumer'],
                                 payload['schema_id'],
                                 payload['perms'],
                                 payload['p_nonce'],
                                 payload['p_sig'],
                                 public_key)

    batcher.process_batch_queue()
