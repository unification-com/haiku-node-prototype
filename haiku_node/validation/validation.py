import os, sys, inspect
from haiku_node.eosio_helpers import eosio_account
from eosapi import Client

currentdir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)


class UnificationACLValidation:

    def __init__(self, conf, requesting_app):
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
        table_data = self.__eosClient.get_table_rows(
            self.__requesting_app,
            self.__conf['acl_contract'], "permrecords", True, 0, -1, -1)

        for i in table_data['rows']:
            if int(i['permission_granted']) == 1:
                self.__granted.append(int(i['user_account']))
            else:
                self.__revoked.append(int(i['user_account']))

    def __call_mother(self):
        json_data = self.__eosClient.get_code(self.__requesting_app)
        code_hash = json_data['code_hash']

        table_data = self.__eosClient.get_table_rows(
            "unif.mother", "unif.mother", "validapps", True, 0, -1, -1)

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
