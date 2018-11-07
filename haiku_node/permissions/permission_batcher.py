import time

from haiku_node.blockchain.eos.uapp import UnificationUapp
from haiku_node.config.config import UnificationConfig
from haiku_node.network.eos import get_ipfs_client, get_eos_rpc_client
from haiku_node.permissions.perm_batch_db import PermissionBatchDatabase
from haiku_node.utils.utils import generate_nonce


class PermissionBatcher:

    def __init__(self, permissions_db):
        self.__pbdb = PermissionBatchDatabase(permissions_db)

    def add_to_queue(self,
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

    def process_batch_queue(self, num=10):
        from haiku_node.permissions.permissions import UnifPermissions

        batch = self.__pbdb.get_unprocessed(num)

        ipfs = get_ipfs_client()
        eos_client = get_eos_rpc_client()

        conf = UnificationConfig()
        provider_uapp = UnificationUapp(eos_client, conf['acl_contract'])
        permissions = UnifPermissions(ipfs, provider_uapp)

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
            is_added = permissions.add_change_request(
                b['consumer_account'], b['end_user_account'], perm_obj)

            b_proc = {
                'op_id': b['op_id'],
                'consumer': b['consumer_account'],
                'is_added': is_added
            }

            processed.append(b_proc)

        ret_data = permissions.process_change_requests()

        for b_p in processed:
            if b_p['is_added']:
                ret_d = ret_data[b_p['consumer']]
                if ret_d['bc']:
                    self.__pbdb.update_processed(
                        b_p['op_id'], proof_tx=ret_d['proof_tx'])

                else:
                    stash_id = self.__pbdb.stash_permission(
                        ret_d['stash']['consumer'],
                        ret_d['stash']['ipfs_hash'],
                        ret_d['stash']['merkle_root'])

                    self.__pbdb.update_processed(b_p['op_id'],
                                                 stash_id=stash_id)
            else:
                # Currently fails if sig is invalid, so delete
                self.__pbdb.delete_op(b_p['op_id'])

        # cleanup stashes
        for c, ret_d in ret_data.items():
            if ret_d['stash_id_committed'] is not None:
                self.__pbdb.update_batch_stashes_with_tx(
                    ret_d['stash_id_committed'], ret_d['proof_tx'])
                self.__pbdb.delete_stash(ret_d['stash_id_committed'])

        print(ret_data)
