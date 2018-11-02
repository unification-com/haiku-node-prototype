import json

from haiku_node.blockchain.ipfs import IPFSDataStore


class UnifPermissions:
    def __init__(self):

        self.__consumer_perms = {}
        self.__updates = {}
        self.__ipfs = IPFSDataStore()

    def load_perms(self, ipfs_hash):
        perms_str = self.__ipfs.cat_file(ipfs_hash)
        self.__consumer_perms = json.loads(perms_str)

    def get_user_perms(self, user_account):
        if user_account in self.__consumer_perms:
            return self.__consumer_perms[user_account]
        else:
            return None

    def add_update(self, consumer, user, perms_obj):
        if consumer not in self.__updates:
            self.__updates[consumer] = {}

        if user not in self.__updates[consumer]:
            self.__updates[consumer][user] = {}

        if perms_obj['schema_id'] not in self.__updates[consumer][user]:
            self.__updates[consumer][user][perms_obj['schema_id']] = {}

        self.__updates[consumer][user][perms_obj['schema_id']] = perms_obj

    # def merge_updates(self):
    #     # Todo

    def get_updates(self):
        return self.__updates

