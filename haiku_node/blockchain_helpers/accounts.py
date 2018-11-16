import json
import logging
import time

import requests
from eosapi import Client
from pathlib import Path

from haiku_node.blockchain.eos.mother import UnificationMother
from haiku_node.blockchain.eos.uapp import UnificationUapp
from haiku_node.blockchain.ipfs import IPFSDataStore
from haiku_node.blockchain_helpers.eos.eos_keys import UnifEosKey
from haiku_node.blockchain_helpers.eos.eosio_cleos import EosioCleos
from haiku_node.client import Provider
from haiku_node.network.eos import (get_cleos,
                                    get_eos_rpc_client, get_ipfs_client)
from haiku_node.permissions.utils import generate_payload
from haiku_node.utils.utils import sha256, generate_nonce

BLOCK_SLEEP = 0.5

log = logging.getLogger(__name__)


class AccountManager:
    def __init__(self, host=False):
        """

        :param host: Set to True if not operating from a Docker container (
        i.e. from the host machine)
        """
        self.cleos = EosioCleos(host)

    def create_key(self):
        log.info('Generating a key')
        ret = self.cleos.run(["create", "key", "--to-console"])

        s = ret.stdout.split('\n')
        private_key = s[0][len('Private key: '):]
        public_key = s[1][len('Public key: '):]

        return public_key, private_key

    def wallet_import_key(self, username, private_key):
        log.info(f"Importing account for {username}")
        self.cleos.run(["wallet", "import",
                        "--name", username,
                        "--private-key", private_key])

    def create_account(self, username, public_key):
        log.info(f"Creating account for {username}")
        ret = self.cleos.run(
            ["create", "account", "eosio", username, public_key, public_key])

        print(ret.stdout)

    def create_account_permissions(self, username, perm_name,
                                   public_key, eosio_code=False):
        log.info(f"Creating permission {perm_name} "
                 f"for {username} with key {public_key}")

        keys = []
        k = {
            "key": public_key,
            "weight": 1
        }

        keys.append(k)

        if eosio_code:
            accounts = []
            actor = {
                'actor': username,
                'permission': 'eosio.code'
            }
            acc = {
                'permission': actor,
                'weight': 1
            }
            accounts.append(acc)
            d = {
                'threshold': 1,
                'keys': keys,
                'accounts': accounts
            }
        else:
            d = {
                'threshold': 1,
                'keys': keys
            }

        ret = self.cleos.run(
            ["set", "account", "permission", username, perm_name,
             json.dumps(d), "active", "-p", f"{username}@active"])

        print(ret.stdout)

    def lock_account_permissions(self, username, smart_contract,
                                 contract_action, perm_name):
        log.info(f"Lock permission {perm_name} for {username} to "
                 f"action {contract_action} in contract {smart_contract}")
        ret = self.cleos.run(["set", "action", "permission", username,
                              smart_contract, contract_action, perm_name,
                              '-p', f'{username}@active'])

        print(ret.stdout)

    def init_permission_structures(self, appnames):
        for consumer in appnames:
            for provider in appnames:
                if consumer != provider:
                    self.init_permission_struct(provider, consumer)

    def init_permission_struct(self, provider, consumer):
        log.debug(f'init_permission_struct Provider'
                  f' {provider}, Consumer {consumer}')
        d = {
            'consumer_id': consumer
        }
        self.cleos.run(
            ['push', 'action', provider, 'initperm',
             json.dumps(d), '-p', f'{consumer}@modreq'])

    def mother_contract(self, username):
        log.info('Associating mother contracts')
        ret = self.cleos.run(
            ["set", "contract", username,
             "/eos/contracts/unification_mother",
             "unification_mother.wasm", "unification_mother.abi",
             "-p", username])

        print(ret.stdout)

    def token_contract(self, username):
        log.info('Associating token contract')
        ret = self.cleos.run(
            ["set", "contract", username,
             "/eos/contracts/eosio.token",
             "eosio.token.wasm", "eosio.token.abi", "-p", username])

        print(ret.stdout)

    def create_und_token(self, maximum_supply):
        log.info('Create UND tokens')
        d = {
            'issuer': 'eosio',
            'maximum_supply': f'{maximum_supply} UND'
        }
        ret = self.cleos.run(
            ['push', 'action', 'unif.token', 'create', json.dumps(d), '-p',
             'unif.token'])

        print(ret.stdout)

    def issue_unds(self, app_config, appname):
        app_conf = app_config[appname]
        quantity = "{0:.4f}".format(round(float(
            app_conf['und_rewards']['start_balance']), 4))

        log.info(f'Issue 100 UND tokens to {appname}')

        d = {
            'to': appname,
            'quantity': f'{quantity} UND',
            'memo': 'memo'
        }
        ret = self.cleos.run(
            ['push', 'action', 'unif.token', 'issue', json.dumps(d), '-p',
             'eosio'])

        print(ret.stdout)

    def associate_contracts(self, username):
        log.info('Associating UApp contracts')
        ret = self.cleos.run(["set", "contract", username,
                              "/eos/contracts/unification_uapp",
                              "unification_uapp.wasm", "unification_uapp.abi",
                              "-p", username])
        print(ret.stdout)

    def set_schema(self, app_config, appname):
        app_conf = app_config[appname]
        for i in app_conf['db_schemas']:
            d = {
                'schema': json.dumps(i['schema']),
                'schema_vers': 1,
                'schedule': 1,
                'price_sched': i['price_sched'],
                'price_adhoc': i['price_adhoc']
            }

            ret = self.cleos.run(
                ['push', 'action', appname, 'addschema', json.dumps(d), '-p',
                 f'{appname}@modschema'])

            print(ret.stdout)

    def get_und_rewards(self, appname : str) -> float:
        ret = self.cleos.run(
            ['get', 'currency', 'balance', 'unif.token', appname, 'UND'])
        stripped = ret.stdout.strip()

        embed_postfix = ' UND'
        if stripped.endswith(embed_postfix):
            stripped = stripped[:-(len(embed_postfix))]
        else:
            raise Exception(f"Unexpected postfix: {stripped}")

        return float(stripped)

    def get_code_hash(self, appname):
        ret = self.cleos.run(['get', 'code', appname])
        return ret.stdout.strip()[len('code hash: '):]

    def add_to_mother(self, app_config, appname,
                      unif_mother_private_key):
        contract_hash = self.get_code_hash(appname)
        ipfs_client = get_ipfs_client()

        app_conf = app_config[appname]
        schema_vers = ""
        for i in app_conf['db_schemas']:
            # hard-code version num to 1 for demo
            schema_vers = schema_vers + i['schema_name'] + ":1,"

            schema_vers = schema_vers.rstrip(",")

            uapp_data = {
                'acl_contract_acc': appname,
                'schema_vers': schema_vers,
                'acl_contract_hash': contract_hash,
                'rpc_server_ip': app_conf['rpc_server'],
                'rpc_server_port': app_conf['rpc_server_port'],
                'name': app_conf['uapp_name'],
                'description': app_conf['uapp_desc'],
                'website': app_conf['uapp_website'],
                'nonce': generate_nonce(16),
                'time_added': int(time.time()),
                'time_updated': int(time.time())
            }

            eosk = UnifEosKey(unif_mother_private_key)
            digest_sha = sha256(json.dumps(uapp_data).encode('utf-8'))

            mother_sig = eosk.sign(digest_sha)

            mother_data = {
                'data': uapp_data,
                'sig': mother_sig
            }

            mother_json = json.dumps(mother_data)

            ipfs_hash = ipfs_client.add_json(mother_json)

            d = {
                'acl_contract_acc': appname,
                'ipfs_hash': ipfs_hash
            }

            ret = self.cleos.run(
            ['push', 'action', 'unif.mother', 'addnew', json.dumps(d),
             '-p', 'unif.mother'])
            print(ret.stdout)

    def validate_with_mother(self, appname):
        d = {
            'acl_contract_acc': appname
        }
        return self.cleos.run(
            ['push', 'action', 'unif.mother', 'validate', json.dumps(d),
             '-p', 'unif.mother'])

    def invalidate_with_mother(self, appname):
        d = {
            'acl_contract_acc': appname
        }
        return self.cleos.run(
            ['push', 'action', 'unif.mother', 'invalidate', json.dumps(d),
             '-p', 'unif.mother'])

    def set_rsa_pub_key_hash(self, public_key_hash, provider):
        d = {
            'rsa_key': public_key_hash
        }
        return self.cleos.run(
            ['push', 'action', provider, 'setrsakey', json.dumps(d),
             '-p', f'{provider}@modrsakey'])

    def request_permission_change(self, user,
                                  app_permission_list, private_key):
        log.info(f"Process {user} permission change requests")
        for consumer, providers in app_permission_list.items():
            for provider, permissions in providers.items():
                granted = permissions['granted']
                if granted:
                    fields = permissions['fields']
                else:
                    fields = ''
                schema_id = int(permissions['schema_id'])

                log.debug(f'request_permission_change '
                          f'{user} requesting {provider} '
                          f'update perms for {consumer} '
                          f'in schema {schema_id}: {granted} {fields}')

                payload, p_nonce, p_sig = generate_payload(user, private_key,
                                                           provider, consumer,
                                                           fields, 'active',
                                                           schema_id)

                log.debug(f'request_permission_change payload: '
                          f'{json.dumps(payload)}')

                mother = UnificationMother(get_eos_rpc_client(), provider,
                                           get_cleos(), get_ipfs_client())
                provider_obj = Provider(provider, 'https', mother)
                url = f"{provider_obj.base_url()}/modify_permission"

                r = requests.post(url, json=payload, verify=False)

                d = r.json()

                if r.status_code != 200:
                    raise Exception(d['message'])

                proc_id = d['proc_id']
                ret_app = d['app']

                log.debug(f"request_permission_change success: "
                          f"{ret_app}: Process ID {proc_id}")

    def run_test_mother(self, app, demo_apps):
        print("Contacting MOTHER FOR: ", app)

        eos_client = Client(nodes=[self.cleos.get_nodeos_url()])
        um = UnificationMother(eos_client, app, get_cleos(),
                               get_ipfs_client())
        print("Valid app: ", um.valid_app())
        assert um.valid_app() is True

        print("UApp SC Hash in MOTHER: ", um.get_hash_in_mother())
        print("Deployed UApp SC hash: ", um.get_deployed_contract_hash())
        assert um.get_hash_in_mother() == um.get_deployed_contract_hash()

        print("Valid Code: ", um.valid_code())
        assert um.valid_code() is True

        print("Signed by MOTHER: ", um.signed_by_mother())
        assert um.signed_by_mother() is True

        print("RPC IP: ", um.get_haiku_rpc_ip())
        assert um.get_haiku_rpc_ip() == demo_apps[app]['rpc_server']

        print("RPC Port: ", um.get_haiku_rpc_port())
        assert int(um.get_haiku_rpc_port()) == int(
            demo_apps[app]['rpc_server_port'])

        print("RPC Server: ", um.get_haiku_rpc_server())
        print("-----------------------------------")

    def run_test_uapp(self, app, demo_apps, appnames):
        print("Loading UApp Contract for: ", app)

        eos_client = Client(nodes=[self.cleos.get_nodeos_url()])
        u_uapp = UnificationUapp(eos_client, app)

        print("Data Schemas:")
        print(u_uapp.get_all_db_schemas())

        print("-----------------------------------")


def make_default_accounts(
        manager: AccountManager, demo_config, appnames, usernames):
    demo_apps = demo_config['demo_apps']
    test_net = demo_config['test_net']

    unif_mother_private_key = None

    for username in usernames + appnames:
        manager.cleos.open_wallet(username)
        password = demo_config['wallet_passwords'][username]['wallet_password']
        manager.cleos.unlock_wallet(username, password)

    keys = [manager.create_key() for x in range(len(usernames + appnames))]

    for username, keys in zip(usernames + appnames, keys):
        manager.wallet_import_key(username, keys[1])
        manager.create_account(username, keys[0])
        if username == 'unif.mother':
            unif_mother_private_key = keys[1]

    print("Wait for transactions to process")
    time.sleep(BLOCK_SLEEP)
    manager.mother_contract('unif.mother')

    print("Wait for transactions to process")
    time.sleep(BLOCK_SLEEP)
    manager.token_contract('unif.token')

    print("Wait for transactions to process")
    time.sleep(BLOCK_SLEEP)
    manager.create_und_token(test_net['maximum_supply'])

    print("Wait for transactions to process")
    time.sleep(BLOCK_SLEEP)

    for appname in appnames:
        manager.associate_contracts(appname)
        print("Wait for transactions to process")
        time.sleep(BLOCK_SLEEP)

        # Permission levels
        print(f"Create account permissions for app {appname}")
        # account permissions to be created
        app_account_perms = ['modschema', 'modreq', 'modrsakey']

        # smart contract actions the permissions are allowed to use
        modschema_actions = ['addschema', 'editschema', 'setvers',
                             'setschedule', 'setminund', 'setschema']
        modreq_actions = ['initreq', 'updatereq']
        modrsakey_actions = ['setrsakey']
        
        for app_account_perm in app_account_perms:
            pub_key, priv_key = manager.create_key()
            manager.wallet_import_key(appname, priv_key)
            manager.create_account_permissions(appname,
                                               app_account_perm, pub_key)

            if app_account_perm == 'modschema':
                contract_actions = modschema_actions
            elif app_account_perm == 'modreq':
                contract_actions = modreq_actions
                manager.create_account_permissions(appname, app_account_perm,
                                                   pub_key, True)
            elif app_account_perm == 'modrsakey':
                contract_actions = modrsakey_actions
            else:
                contract_actions = []

            for contract_action in contract_actions:
                manager.lock_account_permissions(appname, appname,
                                                 contract_action,
                                                 app_account_perm)

            # ToDo: This is probably better suited as a
            #  temporary assignment, set in the client
            if app_account_perm == 'modreq':
                # need to set for initperm for consumer in provider contracts
                for prov_app in appnames:
                    if prov_app != appname:
                        manager.lock_account_permissions(appname, prov_app,
                                                         'initperm',
                                                         app_account_perm)
                        time.sleep(BLOCK_SLEEP)

        manager.set_schema(demo_apps, appname)
        print("Wait for transactions to process")
        time.sleep(BLOCK_SLEEP)
        manager.add_to_mother(demo_apps, appname, unif_mother_private_key)
        print("Wait for transactions to process")
        time.sleep(BLOCK_SLEEP)
        manager.issue_unds(demo_apps, appname)
        print("Wait for transactions to process")
        time.sleep(BLOCK_SLEEP)

    manager.init_permission_structures(appnames)

    user_wallet_passwords = demo_config['wallet_passwords']

    for username in usernames:
        # Todo: maybe have sys_users list?
        if username not in ['unif.mother', 'unif.token']:
            print(f"Create account permissions for user {username}")
            pub_key = manager.cleos.get_public_key(username, 'active')
            wallet_pass = user_wallet_passwords[username]['wallet_password']
            priv_key = manager.cleos.get_private_key(username,  wallet_pass,
                                                     pub_key)

            try:
                permission_obj = demo_config['demo_permissions'][username]
                manager.request_permission_change(username,
                                                  permission_obj,
                                                  priv_key)
            except Exception as e:
                log.error(f'request_permission_change Failed with error: {e}')

    print("Wait for transactions to process")
    time.sleep(BLOCK_SLEEP)

    for appname in appnames:
        log.info(f'==========RUN CONTRACT DUMPS FOR {appname}==========')
        manager.run_test_mother(appname, demo_apps)
        manager.run_test_uapp(appname, demo_apps, appnames)
        log.info(f'==========END CONTRACT DUMPS FOR {appname}==========')


def create_public_data(manager: AccountManager, data_path, appnames):
    for appname in appnames:
        time.sleep(BLOCK_SLEEP)
        store = IPFSDataStore()
        public_key_path = data_path / Path(appname) / Path('key.public')
        h = store.add_file(public_key_path)

        manager.set_rsa_pub_key_hash(h, appname)
