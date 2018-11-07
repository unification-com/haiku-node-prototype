import logging
import tempfile

from create_perm_batch_dbs import _create_perm_batch_db

from haiku_node.permissions.permission_batcher import PermissionBatcher

log = logging.getLogger(__name__)


def test_perm_batches():
    f = tempfile.NamedTemporaryFile(mode='w', delete=False)
    log.info(f"Writing to {f.name}")

    _create_perm_batch_db(f.name)
    batch = PermissionBatcher(f.name)
    batch.add_to_queue(
        'user1', 'app1', 0, 'DataBlob', 2558268601041029,
        'SIG_K1_Ka9y9vJzFCHeCxZr8zgV8h38p5tALjYxgdM874d2dnSRd3zeJCspMJJ65rb92V'
        'xyo4XFPzaSFYW8TuN85HaHdS9deNCVnQ',
        'EOS5z4FPxiDmptdPggLxApJQSzNkmsi6wYqNQnc8Y9exZVTcpusQw')
