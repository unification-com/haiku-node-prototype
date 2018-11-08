import logging
import tempfile

from unittest.mock import patch, MagicMock

from create_perm_batch_dbs import _create_perm_batch_db

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

    batch = PermissionBatcher(f.name)
    batch.add_to_queue(
        'user1', 'app1', 0, 'DataBlob', 2558268601041029,
        'SIG_K1_Ka9y9vJzFCHeCxZr8zgV8h38p5tALjYxgdM874d2dnSRd3zeJCspMJJ65r'
        'b92Vxyo4XFPzaSFYW8TuN85HaHdS9deNCVnQ',
        'EOS5z4FPxiDmptdPggLxApJQSzNkmsi6wYqNQnc8Y9exZVTcpusQw')

    batch.process_batch_queue()
