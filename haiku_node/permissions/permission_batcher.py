import logging
import time

from haiku_node.blockchain.eos.uapp import get_self_uapp
from haiku_node.network.eos import get_ipfs_client
from haiku_node.permissions.perm_batch_db import PermissionBatchDatabase
from haiku_node.permissions.permissions import UnifPermissions
from haiku_node.utils.utils import generate_nonce


log = logging.getLogger(__name__)


class PermissionBatcher:

    def __init__(self, permissions_db):
        self.db = PermissionBatchDatabase(permissions_db)
        self.ipfs = get_ipfs_client()

    def add_to_queue(self, *kwargs):
        return self.db.add(*kwargs)

    def process_batch_queue(self, num=10):

        provider_uapp = get_self_uapp()
        permissions = UnifPermissions(self.ipfs, provider_uapp)

        processed = []

        for item in self.db.get_unprocessed(num):
            perm = {
                'perms': item['perms'],
                'p_nonce': item['p_nonce'],
                'p_sig': item['p_sig'],
                'pub_key': item['pub_key'],
                'schema_id': item['schema_id'],
                'consumer': item['consumer_account'],
                'user': item['end_user_account'],
                'b_nonce': generate_nonce(16),
                'b_time': time.time()
            }
            is_added = permissions.add_change_request(
                item['consumer_account'], item['end_user_account'], perm)

            b_proc = {
                'op_id': item['op_id'],
                'consumer': item['consumer_account'],
                'is_added': is_added
            }

            processed.append(b_proc)

        ret_data = permissions.process_change_requests()

        for item in processed:
            if item['is_added']:
                ret_d = ret_data[item['consumer']]
                if ret_d['bc']:
                    self.db.update_processed(
                        item['op_id'], proof_tx=ret_d['proof_tx'])

                else:
                    stash_id = self.db.stash_permission(
                        ret_d['stash']['consumer'],
                        ret_d['stash']['ipfs_hash'],
                        ret_d['stash']['merkle_root'])

                    self.db.update_processed(item['op_id'],
                                             stash_id=stash_id)
            else:
                # Currently fails if sig is invalid, so delete
                self.db.delete_op(item['op_id'])

        # cleanup stashes
        for c, ret_d in ret_data.items():
            if ret_d['stash_id_committed'] is not None:
                self.db.update_batch_stashes_with_tx(
                    ret_d['stash_id_committed'], ret_d['proof_tx'])
                self.db.delete_stash(ret_d['stash_id_committed'])

        log.debug(ret_data)
