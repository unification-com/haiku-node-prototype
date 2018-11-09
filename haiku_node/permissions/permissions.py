import json

from haiku_node.blockchain.eos.uapp import UnificationUapp
from haiku_node.blockchain.ipfs import IPFSDataStore
from haiku_node.blockchain_helpers.eos.eos_keys import UnifEosKey
from haiku_node.config.config import UnificationConfig
from haiku_node.network.eos import get_eos_rpc_client
from haiku_node.utils.utils import generate_perm_digest_sha


class UnifPermissions:
    def __init__(self):

        self.__consumer_perms = {}
        self.__updates = {}
        self.__ipfs = IPFSDataStore()

        conf = UnificationConfig()
        eos_client = get_eos_rpc_client()
        self.__provider_uapp = UnificationUapp(eos_client, conf['acl_contract'])

    def __verify_update(self, perm_obj):
        perm_digest_sha = generate_perm_digest_sha(perm_obj['perms'], perm_obj['schema_id'], perm_obj['p_nonce'], perm_obj['consumer'])
        eosk = UnifEosKey()
        return eosk.verify_pub_key(perm_obj['p_sig'], perm_digest_sha, perm_obj['pub_key'])

    def __merge_updates(self, current_perms_hash, new_perms):
        current_permissions = json.loads(self.__ipfs.get_json(current_perms_hash))
        new_perms = {**current_permissions, **new_perms}
        return new_perms

    def load_perms(self, ipfs_hash):
        perms_str = self.__ipfs.get_json(ipfs_hash)
        self.__consumer_perms = json.loads(perms_str)

    def get_user_perms(self, user_account):
        if user_account in self.__consumer_perms:
            return self.__consumer_perms[user_account]
        else:
            return None

    def add_update(self, consumer, user, perms_obj):
        if self.__verify_update(perms_obj):
            if consumer not in self.__updates:
                self.__updates[consumer] = {}

            if user not in self.__updates[consumer]:
                self.__updates[consumer][user] = {}

            if perms_obj['schema_id'] not in self.__updates[consumer][user]:
                self.__updates[consumer][user][perms_obj['schema_id']] = {}

            self.__updates[consumer][user][perms_obj['schema_id']] = perms_obj

            return True
        else:
            return False

    def process(self):
        consumer_txs = {}
        for consumer, perms in self.__updates.items():
            ipfs_hash, merkle_root = self.__provider_uapp.get_ipfs_perms_for_req_app(consumer)
            d = {}

            if ipfs_hash is None:
                print("no Provider -> Consumer relationship yet. Add to tmp storage")
                # ToDo: move to temporary storage, until Consumer makes request. Then process.
                d['bc'] = False
                d['proof_tx'] = None
                d['stash_id'] = None
            elif ipfs_hash == '0000000000000000000000000000000000000000000000':
                # relationship established, but not permissions stored yet
                perms_json_str = json.dumps(perms)
                new_ipfs_hash = self.__ipfs.add_json(perms_json_str)
                # ToDo: Merkle tree
                new_merkle_root = '0000000000000000000000000000000000000000000000'

                tx_id = self.__provider_uapp.update_userperms(consumer, new_ipfs_hash, new_merkle_root)

                d['bc'] = True
                d['proof_tx'] = tx_id
                d['stash_id'] = None
            else:
                # update existing permissions
                print("update existing permissions")
                new_perms = self.__merge_updates(ipfs_hash, perms)
                perms_json_str = json.dumps(new_perms)
                new_ipfs_hash = self.__ipfs.add_json(perms_json_str)
                # ToDo: Merkle tree
                new_merkle_root = '0000000000000000000000000000000000000000000000'

                tx_id = self.__provider_uapp.update_userperms(consumer, new_ipfs_hash, new_merkle_root)

                d['bc'] = True
                d['proof_tx'] = tx_id
                d['stash_id'] = None

            consumer_txs[consumer] = d

        return consumer_txs

    def get_updates(self):
        return self.__updates