import json
import os, sys, inspect
from eosio_helpers import eosio_account
from eosapi import Client

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)


class UnificationACLValidation:

    def __init__(self, requesting_app):
        self.requesting_app = requesting_app
        self.is_valid_app = False
        self.is_valid_code = False
        self.granted = []
        self.revoked = []

        with open(parentdir + '/config/config.json') as f:
            self.conf = json.load(f)

        self.eosClient = Client(nodes=['http://' + self.conf['eos_rpc_ip'] + ':' + self.conf['eos_rpc_port']])

        self._run()

    def app_has_user_permission(self, user_account):
        has_permission = False

        user_acc_uint64 = eosio_account.string_to_name(user_account)

        if user_acc_uint64 in self.granted:
            has_permission = True

        return has_permission

    def users_granted(self):
        return self.granted

    def users_revoked(self):
        return self.revoked

    def valid_app(self):
        return self.is_valid_app

    def valid_code(self):
        return self.is_valid_code

    def _run(self):
        self._call_mother()
        if self.is_valid_app and self.is_valid_code:
            self._get_app_permissions()

    def _get_app_permissions(self):
        table_data = self.eosClient.get_table_rows(self.requesting_app, self.conf['acl_contract'], "unifacl", True, 0,
                                                   -1, -1)

        for i in table_data['rows']:
            if int(i['permission_granted']) == 1:
                self.granted.append(int(i['user_account']))
            else:
                self.revoked.append(int(i['user_account']))

    def _call_mother(self):
        json_data = self.eosClient.get_code(self.requesting_app)
        code_hash = json_data['code_hash']

        table_data = self.eosClient.get_table_rows("unif.mother", "unif.mother", "validapps", True, 0, -1, -1)

        req_app_uint64 = eosio_account.string_to_name(self.requesting_app)

        for i in table_data['rows']:
            if int(i['acl_contract_acc']) == req_app_uint64 and int(i['is_valid']) == 1:
                self.is_valid_app = True
            if int(i['acl_contract_acc']) == req_app_uint64 and i['acl_contract_hash'] == code_hash:
                self.is_valid_code = True

