import time

from haiku_node.permissions.perm_batch_db import (
    PermissionBatchDatabase, default_db as pb_db)
from haiku_node.utils.utils import generate_nonce


class PermissionBatcher:

    def __init__(self):
        self.__pbdb = PermissionBatchDatabase(pb_db())

    def add(self,
            user_account,
            consumer_account,
            schema_id,
            perms,
            p_nonce,
            p_sig,
            pub_key,
            bc_type='eos'):

        return self.__pbdb.add(user_account,
                               consumer_account,
                               schema_id,
                               perms,
                               p_nonce,
                               p_sig,
                               pub_key,
                               bc_type)

    def process_batch(self, num=10):
        from haiku_node.permissions.permissions import UnifPermissions

        batch = self.__pbdb.get_unprocessed(num)
        permissions = UnifPermissions()

        processed = []

        for b in batch:
            perm_obj = {
                'perms': b['perms'],
                'p_nonce': b['p_nonce'],
                'p_sig': b['p_sig'],
                'pub_key': b['pub_key'],
                'schema_id': b['schema_id'],
                'consumer': b['consumer_account'],
                'user': b['end_user_account'],
                'b_nonce': generate_nonce(16),
                'b_time': time.time()
            }
            is_added = permissions.add_update(b['consumer_account'], b['end_user_account'], perm_obj)

            b_proc = {
                'op_id': b['op_id'],
                'consumer': b['consumer_account'],
                'is_added': is_added
            }

            processed.append(b_proc)

        ret_data = permissions.process()

        for b_p in processed:
            if b_p['is_added']:
                ret_d = ret_data[b_p['consumer']]
                if ret_d['bc']:
                    self.__pbdb.update_processed(b_p['op_id'], proof_tx=ret_d['proof_tx'])
                else:
                    stash_id = self.__pbdb.stash_permission(ret_d['stash']['consumer'],
                                                     ret_d['stash']['ipfs_hash'],
                                                     ret_d['stash']['merkle_root'])

                    self.__pbdb.update_processed(b_p['op_id'], stash_id=stash_id)
            else:
                # Currently fails if sig is invalid, so delete
                self.__pbdb.delete_op(b_p['op_id'])

        print(ret_data)
