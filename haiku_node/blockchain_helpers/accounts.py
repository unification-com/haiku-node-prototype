import json
import logging
import time

from pathlib import Path
from eosapi import Client

from haiku_node.blockchain.ipfs import IPFSDataStore
from haiku_node.blockchain.mother import UnificationMother
from haiku_node.blockchain.uapp import UnificationUapp
from haiku_node.blockchain_helpers.eosio_cleos import EosioCleos


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
        self.cleos.run(["wallet", "import", "-n", username, private_key])

    def create_account(self, username, public_key):
        log.info(f"Creating account for {username}")
        ret = self.cleos.run(
            ["create", "account", "eosio", username, public_key, public_key])

        print(ret.stdout)

    def create_account_permissions(self, username, perm_name, public_key):
        log.info(f"Creating permission {perm_name} for {username} with key {public_key}")

        keys = []
        k = {
            "key": public_key,
            "weight": 1
        }

        keys.append(k)

        d = {
            'threshold': 1,
            'keys': keys
        }

        ret = self.cleos.run(
            ["set", "account", "permission", username, perm_name,
             json.dumps(d), "active", "-p", f"{username}@active"])

        print(ret.stdout)

    def lock_account_permissions(self, username, smart_contract, contract_action, perm_name):
        log.info(f"Lock permission {perm_name} for {username} to action {contract_action} in contract {smart_contract}")
        ret = self.cleos.run(["set", "account", "permission", username,
                          smart_contract, contract_action, perm_name])

        print(ret.stdout)

    def mother_contract(self, username):
        log.info('Associating mother contracts')
        ret = self.cleos.run(
            ["set", "contract", username,
             "/eos/contracts/unification_mother",
             "/eos/contracts/unification_mother/unification_mother.wast",
             "/eos/contracts/unification_mother/unification_mother.abi",
             "-p", username])

        print(ret.stdout)

    def token_contract(self, username):
        log.info('Associating token contract')
        ret = self.cleos.run(
            ["set", "contract", username,
             "/eos/contracts/eosio.token",
             "/eos/contracts/eosio.token/eosio.token.wast",
             "/eos/contracts/eosio.token/eosio.token.abi",
             "-p", username])

        print(ret.stdout)

    def create_und_token(self):
        log.info('Create UND tokens')
        # TODO: migrate maximum_supply to demo_config.json
        d = {
            'issuer': 'eosio',
            'maximum_supply': '1000000000.0000 UND'
        }
        ret = self.cleos.run(
            ['push', 'action', 'unif.token', 'create', json.dumps(d), '-p',
             'unif.token'])

        print(ret.stdout)

    def issue_unds(self, app_config, appname):
        app_conf = app_config[appname]
        quantity = "{0:.4f}".format(round(float(app_conf['und_rewards']['start_balance']), 4))
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
                          "/eos/contracts/unification_uapp/unification_uapp.wast",
                          "/eos/contracts/unification_uapp/unification_uapp.abi",
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
            # ret = self.cleos.run(
            #     ['push', 'action', appname, 'addschema', json.dumps(d), '-p',
            #      f'{appname}@modschema'])
            ret = self.cleos.run(
                ['push', 'action', appname, 'addschema', json.dumps(d), '-p',
                 appname])
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

    def add_to_mother(self, app_config, appname):
        contract_hash = self.get_code_hash(appname)

        app_conf = app_config[appname]
        schema_vers = ""
        for i in app_conf['db_schemas']:
            # hard-code version num to 1 for demo
            schema_vers = schema_vers + i['schema_name'] + ":1,"

            schema_vers = schema_vers.rstrip(",")

            d = {
                'acl_contract_acc': appname,
                'schema_vers': schema_vers,
                'acl_contract_hash': contract_hash,
                'rpc_server_ip': app_conf['rpc_server'],
                'rpc_server_port': app_conf['rpc_server_port']
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

    def grant(self, provider, requester, user):
        d = {
            'user_account': user,
            'requesting_app': requester,
            'level': 1
        }
        return self.cleos.run(
            ['push', 'action', provider, 'modifyperm', json.dumps(d), '-p', user])

    def set_rsa_pub_key_hash(self, public_key_hash, provider):
        d = {
            'rsa_key': public_key_hash
        }
        return self.cleos.run(
            ['push', 'action', provider, 'setrsakey', json.dumps(d), '-p', provider])
        # return self.cleos.run(
        #     ['push', 'action', provider, 'setrsakey', json.dumps(d), '-p', f'{provider}@modrsakey'])

    def revoke(self, provider, requester, user):
        d = {
            'user_account': user,
            'requesting_app': requester,
            'level': 0
        }
        return self.cleos.run(
            ['push', 'action', provider, 'modifyperm', json.dumps(d), '-p', user])

    def set_permissions(self, demo_permissions):
        print("set_permissions")
        for user_perms in demo_permissions['permissions']:
            user = user_perms['user']
            for haiku in user_perms['haiku_nodes']:
                app = haiku['app']
                for req_app in haiku['req_apps']:
                    if req_app['granted']:
                        self.grant(app, req_app['account'], user)
                    else:
                        self.revoke(app, req_app['account'], user)
            print("Wait for transactions to process")
            time.sleep(BLOCK_SLEEP)

    def run_test_mother(self, app, demo_apps):
        print("Contacting MOTHER FOR: ", app)

        eos_client = Client(nodes=[self.cleos.get_nodeos_url()])
        um = UnificationMother(eos_client, app)
        print("Valid app: ", um.valid_app())
        assert um.valid_app() is True

        print("UApp SC Hash in MOTHER: ", um.get_hash_in_mother())
        print("Deployed UApp SC Contract hash: ", um.get_deployed_contract_hash())
        assert um.get_hash_in_mother() == um.get_deployed_contract_hash()

        print("Valid Code: ", um.valid_code())
        assert um.valid_code() is True

        print("RPC IP: ", um.get_haiku_rpc_ip())
        assert um.get_haiku_rpc_ip() == demo_apps[app]['rpc_server']

        print("RPC Port: ", um.get_haiku_rpc_port())
        assert int(um.get_haiku_rpc_port()) == int(
            demo_apps[app]['rpc_server_port'])

        print("RPC Server: ", um.get_haiku_rpc_server())
        print("-----------------------------------")

    def run_test_uapp(self, app, demo_apps, appnames):
        print("Loading UApp Contract for: ", app)

        eosClient = Client(nodes=[self.cleos.get_nodeos_url()])
        u_uapp = UnificationUapp(eosClient, app)

        print("Data Schemas:")
        print(u_uapp.get_all_db_schemas())

        print("Check Permissions")
        for req_app in appnames:
            print("Check perms for Requesting App: ", req_app)
            granted, revoked = u_uapp.get_perms_for_req_app(req_app)
            print("Users who Granted:")
            print(granted)
            print("Users who Revoked:")
            print(revoked)

        print("-----------------------------------")


def make_default_accounts(
        manager: AccountManager, demo_config, appnames, usernames):
    demo_apps = demo_config['demo_apps']
    demo_permissions = demo_config['demo_permissions']

    for username in usernames + appnames:
        manager.cleos.open_wallet(username)
        password = demo_config['wallet_passwords'][username]['wallet_password']
        manager.cleos.unlock_wallet(username, password)

    keys = [manager.create_key() for x in range(len(usernames + appnames))]

    for username, keys in zip(usernames + appnames, keys):
        manager.wallet_import_key(username, keys[1])
        manager.create_account(username, keys[0])


    print("Wait for transactions to process")
    time.sleep(BLOCK_SLEEP)
    manager.mother_contract('unif.mother')

    print("Wait for transactions to process")
    time.sleep(BLOCK_SLEEP)
    manager.token_contract('unif.token')

    print("Wait for transactions to process")
    time.sleep(BLOCK_SLEEP)
    manager.create_und_token()

    print("Wait for transactions to process")
    time.sleep(BLOCK_SLEEP)

    for appname in appnames:
        manager.associate_contracts(appname)
        print("Wait for transactions to process")
        time.sleep(BLOCK_SLEEP)

        # Permission levels
        print(f"Create account permissions for app {appname}")
        # account permissions to be created
        app_account_perms = ['modschema', 'modperms', 'modreq', 'modrsakey']

        # smart contract actions the permissions are allowed to use
        modschema_actions = ['addschema', 'editschema', 'setvers', 'setschedule', 'setminund', 'setschema']
        modperms_actions = ['modifyperm', 'modifypermsg']
        modreq_actions = ['initreq', 'updatereq']
        modrsakey_actions = ['setrsakey']
        
        for app_account_perm in app_account_perms:
            pub_key, priv_key = manager.create_key()
            manager.wallet_import_key(appname, priv_key)
            manager.create_account_permissions(appname, app_account_perm, pub_key)

            if app_account_perm == 'modschema':
                contract_actions = modschema_actions
            elif app_account_perm == 'modperms':
                contract_actions = modperms_actions
            elif app_account_perm == 'modreq':
                contract_actions = modreq_actions
            elif app_account_perm == 'modrsakey':
                contract_actions = modrsakey_actions
            else:
                contract_actions = []

            for contract_action in contract_actions:
                manager.lock_account_permissions(appname, appname, contract_action, app_account_perm)

        manager.set_schema(demo_apps, appname)
        print("Wait for transactions to process")
        time.sleep(BLOCK_SLEEP)
        manager.add_to_mother(demo_apps, appname)
        print("Wait for transactions to process")
        time.sleep(BLOCK_SLEEP)
        manager.issue_unds(demo_apps, appname)

    for username in usernames:
        if username not in ['unif.mother', 'unif.token']:  # Todo: maybe have sys_users list?
            print(f"Create account permissions for user {username}")
            pub_key, priv_key = manager.create_key()
            manager.wallet_import_key(username, priv_key)
            manager.create_account_permissions(username, 'modperms', pub_key)


    print("Wait for transactions to process")
    time.sleep(BLOCK_SLEEP)
    manager.set_permissions(demo_permissions)

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
