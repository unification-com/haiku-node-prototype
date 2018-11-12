import logging
import json

from haiku_node.blockchain_helpers.eos.eos_keys import UnifEosKey
from haiku_node.encryption.merkle.merkle_tree import MerkleTree, MerkleException
from haiku_node.utils.utils import generate_perm_digest_sha
from haiku_node.permissions.perm_batch_db import (
    PermissionBatchDatabase, default_db as pb_db)

ZERO_MASK = '0000000000000000000000000000000000000000000000'


log = logging.getLogger(__name__)


class UnifPermissions:

    def __init__(self, ipfs, provider_uapp):
        self.__consumer_perms = {}
        self.__change_requests = {}
        self.__ipfs = ipfs
        self.__uapp = provider_uapp

    def add_change_request(self, consumer, user, perms_obj: dict):
        if self.__verify_change_request(perms_obj):
            if consumer not in self.__change_requests:
                self.__change_requests[consumer] = {}

            if user not in self.__change_requests[consumer]:
                self.__change_requests[consumer][user] = {}

            if perms_obj['schema_id'] not in self.__change_requests[consumer][
                user]:
                self.__change_requests[consumer][user][
                    perms_obj['schema_id']] = {}

            self.__change_requests[consumer][user][
                perms_obj['schema_id']] = perms_obj

            return True
        else:
            return False

    def process_change_requests(self):
        permission_db = PermissionBatchDatabase(pb_db())

        consumer_txs = {}
        for consumer, perms in self.__change_requests.items():
            ipfs_hash, merkle_root = self.__uapp.get_ipfs_perms_for_req_app(
                consumer)
            # defaults
            d = {
                'bc': False,
                'proof_tx': None,
                'stash': None,
                'stash_id_committed': None
            }

            if ipfs_hash is None:
                log.info("no Provider -> Consumer relationship yet. "
                         "Add to tmp storage")

                latest_stash = permission_db.get_stash(consumer)

                if latest_stash is not None:
                    # merge with latest stash
                    perms = self.__merge_change_requests(
                        latest_stash['ipfs_hash'], perms)

                perms_json_str = json.dumps(perms)
                new_ipfs_hash = self.__ipfs.add_json(perms_json_str)

                new_merkle_root = self.__generate_merkle(perms)
                stash = {
                    'consumer': consumer,
                    'ipfs_hash': new_ipfs_hash,
                    'merkle_root': new_merkle_root
                }

                d['stash'] = stash

            elif ipfs_hash == ZERO_MASK:
                # relationship established, but not permissions stored yet
                # Probably unnecessary, since this will be done on the first
                # data request...

                # check for stashed permissions
                latest_stash = permission_db.get_stash(consumer)

                if latest_stash is not None:
                    # merge with latest stash
                    perms = self.__merge_change_requests(
                        latest_stash['ipfs_hash'], perms)
                    # flag for deletion
                    d['stash_id_committed'] = latest_stash['stash_id']

                perms_json_str = json.dumps(perms)
                new_ipfs_hash = self.__ipfs.add_json(perms_json_str)
                new_merkle_root = self.__generate_merkle(perms)

                tx_id = self.__uapp.update_userperms(
                    consumer, new_ipfs_hash, new_merkle_root)

                d['bc'] = True
                d['proof_tx'] = tx_id
            else:
                log.info("update existing permissions")
                new_perms = self.__merge_change_requests(ipfs_hash, perms)
                perms_json_str = json.dumps(new_perms)
                new_ipfs_hash = self.__ipfs.add_json(perms_json_str)
                new_merkle_root = self.__generate_merkle(new_perms)

                tx_id = self.__uapp.update_userperms(
                    consumer, new_ipfs_hash, new_merkle_root)

                d['bc'] = True
                d['proof_tx'] = tx_id

            consumer_txs[consumer] = d

        return consumer_txs

    def check_and_process_stashed(self, consumer_account):
        from haiku_node.permissions.perm_batch_db import (
            PermissionBatchDatabase, default_db as pb_db)

        pb = PermissionBatchDatabase(pb_db())

        latest_stash = pb.get_stash(consumer_account)
        if latest_stash is not None:
            tx_id = self.__uapp.update_userperms(
                consumer_account, latest_stash['ipfs_hash'],
                latest_stash['merkle_root'])
            pb.update_batch_stashes_with_tx(latest_stash['stash_id'], tx_id)
            pb.delete_stash(latest_stash['stash_id'])

    def get_change_requests(self):
        return self.__change_requests

    def __verify_change_request(self, perm: dict) -> bool:
        perm_digest_sha = generate_perm_digest_sha(
            perm['perms'], perm['schema_id'],
            perm['p_nonce'], perm['consumer'])

        return UnifEosKey().verify_pub_key(
            perm['p_sig'], perm_digest_sha, perm['pub_key'])

    def __merge_change_requests(self, current_perms_hash, new_perms):
        current_permissions = json.loads(self.__ipfs.get_json(
            current_perms_hash))
        new_perms = {**current_permissions, **new_perms}
        return new_perms

    def __generate_merkle(self, perms):
        tree = MerkleTree()
        for user, perm in perms.items():
            tree.add_leaf(json.dumps(perm))

        tree.grow_tree()

        return tree.get_root_str()

    def load_perms(self, ipfs_hash):
        perms_str = self.__ipfs.get_json(ipfs_hash)
        self.__consumer_perms = json.loads(perms_str)

    def get_user_perms(self, user_account):
        if user_account in self.__consumer_perms:
            return self.__consumer_perms[user_account]
        else:
            return None
