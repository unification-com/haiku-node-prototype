import logging
import tempfile

from unittest.mock import patch, MagicMock

from create_perm_batch_dbs import _create_perm_batch_db

from haiku_node.permissions.permission_batcher import PermissionBatcher

log = logging.getLogger(__name__)


def mock_get_ipfs():
    m = MagicMock()
    m.get_json.return_value = '{}'
    return m


def mock_get_self_uapp():
    m = MagicMock()
    m.get_ipfs_perms_for_req_app.return_value = (0, 0)
    m.update_userperms.return_value = 1
    return m


@patch('haiku_node.permissions.permission_batcher.get_ipfs_client',
       return_value=mock_get_ipfs())
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
