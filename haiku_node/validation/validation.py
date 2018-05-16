import inspect
import os
import sys

from haiku_node.eosio_helpers import eosio_account
from eosapi import Client

currentdir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)


class UnificationACLValidation:

    def __init__(self, conf, requesting_app):
        """
        :param conf: config json object
        :param requesting_app: the eos account name of the requesting app
        """
        self.__mother = "unif.mother"
        self.__valid_apps_table = "validapps"
        self.__permission_rec_table = "permrecords"

        self.__requesting_app = requesting_app
        self.__conf = conf
        self.__eosClient = Client(
            nodes=[f"http://{self.__conf['eos_rpc_ip']}"
                   f":{self.__conf['eos_rpc_port']}"])
        self.__is_valid_app = False
        self.__is_valid_code = False
        self.__granted = []
        self.__revoked = []

        self.__run()

    def app_has_user_permission(self, user_account):
        has_permission = False

        user_acc_uint64 = eosio_account.string_to_name(user_account)

        if user_acc_uint64 in self.__granted:
            has_permission = True

        return has_permission

    def users_granted(self):
        return self.__granted

    def users_revoked(self):
        return self.__revoked

    def valid_app(self):
        return self.__is_valid_app

    def valid_code(self):
        return self.__is_valid_code

    def __run(self):
        self.__call_mother()
        if self.__is_valid_app and self.__is_valid_code:
            self.__get_app_permissions()
        else:
            self.__granted = []
            self.__revoked = []

    def __get_app_permissions(self):
        """
        App checks it's own smart contract to see which users are granted
        permission to access it's data.
        """

        # TODO: run in loop and check JSON result for "more" value
        table_data = self.__eosClient.get_table_rows(
            self.__requesting_app,
            self.__conf['acl_contract'], self.__permission_rec_table, True, 0, -1, -1)

        for i in table_data['rows']:
            if int(i['permission_granted']) == 1:
                self.__granted.append(int(i['user_account']))
            else:
                self.__revoked.append(int(i['user_account']))

    def __call_mother(self):
        """
        Call the Mother Smart Contract, and check if the requesting_app is both
        a verified app, and that it's smart contract code is valid (by checking
        the code's hash).
        """
        json_data = self.__eosClient.get_code(self.__requesting_app)
        code_hash = json_data['code_hash']

        table_data = self.__eosClient.get_table_rows(
            self.__mother, self.__mother, self.__valid_apps_table, True, 0, -1, -1)

        req_app_uint64 = eosio_account.string_to_name(self.__requesting_app)

        for i in table_data['rows']:

            if int(i['acl_contract_acc']) == req_app_uint64 and \
                    int(i['is_valid']) == 1:
                self.__is_valid_app = True

            if int(i['acl_contract_acc']) == req_app_uint64 and \
                    i['acl_contract_hash'] == code_hash:
                self.__is_valid_code = True


if __name__ == '__main__':
    print("Nope.")
