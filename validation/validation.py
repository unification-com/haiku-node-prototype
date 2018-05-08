import json
import requests
import os,sys,inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from esoio_helpers import esoio_account

class UnificationACLValidation:

    def __init__(self):
        with open(parentdir + '/config/config.json') as f:
            self.conf = json.load(f)

    def app_has_user_permission(self, requesting_app, user_account):
        has_permission = False

        url = 'http://' + self.conf['eos_rpc_ip'] + ':' + self.conf['eos_rpc_port'] + '/v1/chain/get_table_rows'
        payload = '{"scope":"' + requesting_app + '", "code":"' + self.conf['acl_contract'] \
                  + '", "table":"unifacl", "json": true}'

        r = requests.post(url, data=payload)
        json_string = r.text

        user_acc_uint64 = esoio_account.string_to_name(user_account)

        table_data = json.loads(json_string)

        for i in table_data['rows']:
            if(int(i['user_account']) == user_acc_uint64 and int(i['permission_granted']) == 1):
                has_permission = True

        return has_permission

    def get_app_allowed_users(self,requesting_app):

        granted = []
        url = 'http://' + self.conf['eos_rpc_ip'] + ':' + self.conf['eos_rpc_port'] + '/v1/chain/get_table_rows'
        payload = '{"scope":"' + requesting_app + '", "code":"' + self.conf['acl_contract']\
                  + '", "table":"unifacl", "json": true}'

        r = requests.post(url, data=payload)
        json_string = r.text
        table_data = json.loads(json_string)
        for i in table_data['rows']:
            if(int(i['permission_granted']) == 1):
                granted.append(int(i['user_account']))

        return granted

    def get_app_revoked_users(self,requesting_app):

        revoked = []
        url = 'http://' + self.conf['eos_rpc_ip'] + ':' + self.conf['eos_rpc_port'] + '/v1/chain/get_table_rows'
        payload = '{"scope":"' + requesting_app + '", "code":"' + self.conf['acl_contract']\
                  + '", "table":"unifacl", "json": true}'

        r = requests.post(url, data=payload)
        json_string = r.text
        table_data = json.loads(json_string)
        for i in table_data['rows']:
            if(int(i['permission_granted']) == 0):
                revoked.append(int(i['user_account']))

        return revoked

