import json
import requests
import os,sys,inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from esoio_helpers import esoio_account
from eosapi import Client

class UnificationACLValidation:

    def __init__(self):
        with open(parentdir + '/config/config.json') as f:
            self.conf = json.load(f)
            self.eosClient = Client(nodes=['http://' + self.conf['eos_rpc_ip'] + ':' + self.conf['eos_rpc_port']])

    def app_has_user_permission(self, requesting_app, user_account):
        has_permission = False

        table_data = self.eosClient.get_table_rows(requesting_app, self.conf['acl_contract'], "unifacl", True, 0, -1, -1)

        user_acc_uint64 = esoio_account.string_to_name(user_account)

        for i in table_data['rows']:
            if(int(i['user_account']) == user_acc_uint64 and int(i['permission_granted']) == 1):
                has_permission = True

        return has_permission

    def get_app_allowed_users(self, requesting_app):

        granted = []

        table_data = self.eosClient.get_table_rows(requesting_app, self.conf['acl_contract'], "unifacl", True, 0, -1, -1)

        for i in table_data['rows']:
            if(int(i['permission_granted']) == 1):
                granted.append(int(i['user_account']))

        return granted

    def get_app_revoked_users(self, requesting_app):

        revoked = []
        table_data = self.eosClient.get_table_rows(requesting_app, self.conf['acl_contract'], "unifacl", True, 0, -1,
                                                   -1)
        for i in table_data['rows']:
            if(int(i['permission_granted']) == 0):
                revoked.append(int(i['user_account']))

        return revoked

    def check_contract_code_hash(self, contract_account, hash):
        code_valid = False
        json_data = self.eosClient.get_code(contract_account)
        code_hash = json_data['code_hash']
        if(hash == code_hash):
            code_valid = True

        return code_valid
