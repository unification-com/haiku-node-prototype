import json
import logging
import subprocess
import time

import requests

from eosapi import Client

from haiku_node.blockchain.acl import UnificationACL
from haiku_node.blockchain.mother import UnificationMother


KEOS_IP = 'keosd'
KEOS_PORT = 8889

NODEOS_IP = 'nodeosd'
NODEOS_PORT = 8888

BLOCK_SLEEP = 0.5

log = logging.getLogger(__name__)


class AccountManager:
    def __init__(self, host=False):
        """

        :param host: Set to True if not operating from a Docker container (
        i.e. from the host machine)
        """
        self.host = host
        if host:
            self.nodeos = f"http://{NODEOS_IP}:{NODEOS_PORT}"
            self.keosd = f"http://127.0.0.1:{KEOS_PORT}"
            self.nodeos_ip = '127.0.0.1'

        else:
            self.nodeos = f"http://{NODEOS_IP}:{NODEOS_PORT}"
            self.keosd = f"http://{KEOS_IP}:{KEOS_PORT}"
            self.nodeos_ip = NODEOS_IP

    def keos_url(self):
        return self.keosd

    def request_keos(self, endpoint):
        return f"{self.keosd}/{endpoint}"

    def cleos(self, subcommands):
        if self.host:
            pre = ["/usr/local/bin/docker", "exec", "keosd",
                   "/opt/eosio/bin/cleos", "--url", self.nodeos,
                   "--wallet-url", self.keosd]
        else:
            pre = ["/opt/eosio/bin/cleos", "--url", self.nodeos,
                   "--wallet-url", self.keosd]

        cmd = pre + subcommands

        log.debug(f"cleos command: {cmd}")

        result = subprocess.run(
            cmd, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, universal_newlines=True)

        log.debug(result.stdout)
        if result.returncode != 0:
            log.warning(result.stdout)
            log.debug(result.stdout)
            log.debug(result.stderr)
            log.debug(' '.join(cmd))

        return result

    def open_wallet(self, username):
        """
        Wallets need to be opened.
        """
        log.info('Opening wallet')
        r = requests.post(self.request_keos('v1/wallet/list_wallets'))
        current_users = [x.strip(' *') for x in r.json()]
        if username not in current_users:
            url = f"{self.keos_url()}/v1/wallet/open"
            r = requests.post(url, data=f""" "{username}" """)
            assert r.status_code == 200

    def create_key(self):
        log.info('Generating a key')
        ret = self.cleos(["create", "key"])

        s = ret.stdout.split('\n')
        private_key = s[0][len('Private key: '):]
        public_key = s[1][len('Public key: '):]

        return public_key, private_key

    def lock_wallet(self, username):
        return self.cleos(["wallet", "lock", "--name", username])

    def unlock_wallet(self, username, password):
        return self.cleos(
            ["wallet", "unlock", "--name", username, "--password", password])

    def wallet_import_key(self, username, private_key):
        log.info(f"Importing account for {username}")
        self.cleos(["wallet", "import", "-n", username, private_key])

    def create_account(self, username, public_key):
        log.info(f"Creating account for {username}")
        ret = self.cleos(
            ["create", "account", "eosio", username, public_key, public_key])

        print(ret.stdout)

    def mother_contract(self, username):
        log.info('Associating mother contracts')
        ret = self.cleos(
            ["set", "contract", username,
             "/eos/contracts/unification_mother",
             "/eos/contracts/unification_mother/unification_mother.wast",
             "/eos/contracts/unification_mother/unification_mother.abi",
             "-p", username])

        print(ret.stdout)

    def associate_contracts(self, username):
        log.info('Associating acl contracts')
        ret = self.cleos(["set", "contract", username,
                          "/eos/contracts/unification_acl",
                          "/eos/contracts/unification_acl/unification_acl.wast",
                          "/eos/contracts/unification_acl/unification_acl.abi",
                          "-p", username])
        print(ret.stdout)

    def set_schema(self, app_config, appname):
        app_conf = app_config[appname]
        for i in app_conf['db_schemas']:
            d = {
                'schema_name': i['schema_name'],
                'schema': i['schema'],
            }
            ret = self.cleos(
                ['push', 'action', appname, 'setschema', json.dumps(d), '-p',
                 appname])
            print(ret.stdout)

    def set_data_sources(self, app_config, appname):
        app_conf = app_config[appname]
        for i in app_conf['data_sources']:
            d = {
                'source_name': i['source_name'],
                'source_type': i['source_type'],
            }
            ret = self.cleos(
                ['push', 'action', appname, 'setsource', json.dumps(d), '-p',
                 appname])
            print(ret.stdout)

    def get_code_hash(self, appname):
        ret = self.cleos(['get', 'code', appname])
        return ret.stdout.strip()[len('code hash: '):]

    def validate_with_mother(self, app_config, appname):
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
            ret = self.cleos(
            ['push', 'action', 'unif.mother', 'validate', json.dumps(d),
             '-p', 'unif.mother'])
            print(ret.stdout)

    def grant(self, provider, requester, user):
        d = {
            'user_account': user,
            'requesting_app': requester,
        }
        return self.cleos(
            ['push', 'action', provider, 'grant', json.dumps(d), '-p', user])

    def revoke(self, provider, requester, user):
        d = {
            'user_account': user,
            'requesting_app': requester,
        }
        return self.cleos(
            ['push', 'action', provider, 'revoke', json.dumps(d), '-p', user])

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

        eos_client = Client(nodes=[f"http://{self.nodeos_ip}:{NODEOS_PORT}"])
        um = UnificationMother(eos_client, app)
        print("Valid app: ", um.valid_app())
        assert um.valid_app() is True

        print("ACL Hash in MOTHER: ", um.get_hash_in_mother())
        print("Deployed ACL Contract hash: ", um.get_deployed_contract_hash())
        assert um.get_hash_in_mother() == um.get_deployed_contract_hash()

        print("Valid Code: ", um.valid_code())
        assert um.valid_code() is True

        print("RPC IP: ", um.get_haiku_rpc_ip())
        assert um.get_haiku_rpc_ip() == demo_apps[app]['rpc_server']

        print("RPC Port: ", um.get_haiku_rpc_port())
        assert int(um.get_haiku_rpc_port()) == int(
            demo_apps[app]['rpc_server_port'])

        print("RPC Server: ", um.get_haiku_rpc_server())
        print("Valid DB Schemas: ")
        print(um.get_valid_db_schemas())
        print("-----------------------------------")

    def run_test_acl(self, app, demo_apps, appnames):
        print("Loading ACL/Meta Contract for: ", app)

        eosClient = Client(nodes=[f"http://{self.nodeos_ip}:{NODEOS_PORT}"])
        u_acl = UnificationACL(eosClient, app)

        print("Data Schemas:")
        print(u_acl.get_db_schemas())
        print("Data Sources:")
        print(u_acl.get_data_sources())

        print("Check Permissions")
        for req_app in appnames:
            print("Check perms for Requesting App: ", req_app)
            granted, revoked = u_acl.get_perms_for_req_app(req_app)
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
        manager.open_wallet(username)
        password = demo_config['wallet_passwords'][username]['wallet_password']
        manager.unlock_wallet(username, password)

    keys = [manager.create_key() for x in range(len(usernames + appnames))]

    for username, keys in zip(usernames + appnames, keys):
        manager.wallet_import_key(username, keys[1])
        manager.create_account(username, keys[0])

    print("Wait for transactions to process")
    time.sleep(BLOCK_SLEEP)
    manager.mother_contract('unif.mother')

    print("Wait for transactions to process")
    time.sleep(BLOCK_SLEEP)

    for appname in appnames:
        manager.associate_contracts(appname)
        print("Wait for transactions to process")
        time.sleep(BLOCK_SLEEP)
        manager.set_schema(demo_apps, appname)
        print("Wait for transactions to process")
        time.sleep(BLOCK_SLEEP)
        manager.set_data_sources(demo_apps, appname)
        print("Wait for transactions to process")
        time.sleep(BLOCK_SLEEP)
        manager.validate_with_mother(demo_apps, appname)

    print("Wait for transactions to process")
    time.sleep(BLOCK_SLEEP)
    manager.set_permissions(demo_permissions)

    print("Wait for transactions to process")
    time.sleep(BLOCK_SLEEP)

    for appname in appnames:
        log.info(f'==========RUN CONTRACT DUMPS FOR {appname}==========')
        manager.run_test_mother(appname, demo_apps)
        manager.run_test_acl(appname, demo_apps, appnames)
        log.info(f'==========END CONTRACT DUMPS FOR {appname}==========')