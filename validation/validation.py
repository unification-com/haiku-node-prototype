import json
import os, sys, inspect
from esoio_helpers import esoio_account
from eosapi import Client

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)


class UnificationACLValidation:

    def __init__(self, requesting_app):
        with open(parentdir + '/config/config.json') as f:
            self.conf = json.load(f)

        self.eosClient = Client(nodes=['http://' + self.conf['eos_rpc_ip'] + ':' + self.conf['eos_rpc_port']])
        self.requesting_app = requesting_app
        self._call_mother()
        self._get_app_permissions()
        self._check_acl_contract_code_hash()

    def app_has_user_permission(self, user_account):
        has_permission = False

        user_acc_uint64 = esoio_account.string_to_name(user_account)

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

    def _check_acl_contract_code_hash(self):
        self.is_valid_code = False
        json_data = self.eosClient.get_code(self.requesting_app)
        code_hash = json_data['code_hash']

        req_app_uint64 = esoio_account.string_to_name(self.requesting_app)

        mother_data = self.eosClient.get_table_rows("unif.mother", "unif.mother", "validapps", True, 0, -1, -1)

        for i in mother_data['rows']:
            if int(i['acl_contract_acc']) == req_app_uint64 and i['acl_contract_hash'] == code_hash:
                self.is_valid_code = True

    def _get_app_permissions(self):
        self.granted = []
        self.revoked = []
        table_data = self.eosClient.get_table_rows(self.requesting_app, self.conf['acl_contract'], "unifacl", True, 0,
                                                   -1, -1)

        for i in table_data['rows']:
            if int(i['permission_granted']) == 1:
                self.granted.append(int(i['user_account']))
            else:
                self.revoked.append(int(i['user_account']))

    def _call_mother(self):
        is_valid = False
        table_data = self.eosClient.get_table_rows("unif.mother", "unif.mother", "validapps", True, 0, -1, -1)

        req_app_uint64 = esoio_account.string_to_name(self.requesting_app)

        for i in table_data['rows']:
            if int(i['acl_contract_acc']) == req_app_uint64 and int(i['is_valid']) == 1:
                is_valid = True

        self.is_valid_app = is_valid
