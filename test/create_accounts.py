import json
import subprocess
import logging

import requests

from eosapi import Client

log = logging.getLogger(__name__)


d = {
    "acl_contract": "app1",
    "eos_rpc_ip": "127.0.0.1",
    "eos_rpc_port": "8888"
}

eosClient = Client(
    nodes=['http://' + d['eos_rpc_ip'] + ':' + d['eos_rpc_port']])


appnames = ['app1', 'app2', 'app3']
usernames = ['user1', 'user2', 'user3', 'unif.mother']


def base_url():
    return f"http://{d['eos_rpc_ip']}:{d['eos_rpc_port']}"


def create_user(username):
    url = f"{base_url()}/v1/wallet/create"
    r = requests.post(url, data=f""" "{username}" """)
    if r.status_code != 201:
        raise Exception(r.content)
    # The response is surrounded in quotation marks
    return r.text[1:-1]


def serialise(xs):
    g = lambda x: '"' + x + '"'
    h = lambda x: '[' + x + ']'
    return h(','.join(map(g, xs)))


def unlock_wallet(username, password):
    url = f"{base_url()}/v1/wallet/unlock"
    r = requests.post(url, data=serialise([username, password]))


def delete_users():
    print('Deleting users')

    cmd = ["/usr/local/bin/docker", "exec", "docker_nodeosd_1", "/bin/bash",
           '-c',
           'rm -f /root/.local/share/eosio/nodeos/data/*.wallet']
    ret = subprocess.check_output(cmd, universal_newlines=True)


def cleos():
    return ["/usr/local/bin/docker", "exec", "docker_nodeosd_1",
            "/opt/eosio/bin/cleos"]


def create_key():
    cmd = cleos() + ["create", "key"]
    ret = subprocess.check_output(cmd, universal_newlines=True)

    s = ret.split('\n')
    private_key = s[0][len('Private key: '):]
    public_key = s[1][len('Public key: '):]

    return public_key, private_key


def wallet_import_key(username, private_key):
    print(f"Importing account for {username}")

    cmd = cleos() + ["wallet", "import", "-n", username, private_key]
    ret = subprocess.check_output(cmd, universal_newlines=True)
    print(ret)


def create_users(names):
    for username in names:
        password = create_user(username)
        print(f"User {username} with password {password}")

        unlock_wallet(username, password)
        print(f"Wallet unlocked")


def create_account(username, public_key):
    cmd = cleos() + ["-v", "create", "account", "eosio", username, public_key,
                     public_key]
    ret = subprocess.check_output(cmd, universal_newlines=True)
    print(ret)


def associate_contracts(username):
    log.info('Associating acl contracts')
    cmd = cleos() + ["set", "contract", username,
                     "/eos/contracts/unification_acl",
                     "/eos/contracts/unification_acl/unification_acl.wast"]
    ret = subprocess.check_output(cmd, universal_newlines=True)
    print(ret)


def mother_contract(username):
    log.info('Associating mother contracts')
    cmd = cleos() + ["set", "contract", username,
                     "/eos/contracts/unification_mother",
                     "/eos/contracts/unification_mother/unification_mother.wast"]
    ret = subprocess.check_output(cmd, universal_newlines=True)
    print(ret)


def set_schema(appname):
    cmd = cleos() + ['push', 'action', appname, 'set.schema',
                     '{"schema":"test1" }', '-p', appname]
    ret = subprocess.check_output(cmd, universal_newlines=True)
    print(ret)


def get_code_hash(appname):
    cmd = cleos() + ['get', 'code', appname]
    ret = subprocess.check_output(cmd, universal_newlines=True)
    return ret.strip()[len('code hash: '):]


def validate_with_mother(appname, contract_hash):
    # TODO: Fix the names

    d = {
        'acl_contract_acc': appname,
        'schema_vers': 1,
        'acl_contract_hash': contract_hash,
        'app_name': 'Unif Test 1',
        'desc': 'Test app 1',
        'server_ip': '127.0.0.1'
    }
    cmd = cleos() + ['push', 'action', 'unif.mother', 'validate', json.dumps(d),
                     '-p', 'unif.mother']
    ret = subprocess.check_output(cmd, universal_newlines=True)


def grant_access():
    print('Granting access')
    d = {
        'user_account': 'user1',
        'requesting_app': 'app2'
    }
    # TODO: Notice the app1 in here
    cmd = cleos() + ['push', 'action', 'app1', 'grant', json.dumps(d), '-p',
                     'user1']
    ret = subprocess.check_output(cmd, universal_newlines=True)


def deny_access():
    d = {
        'user_account': 'user3',
        'requesting_app': 'app2'
    }
    # TODO: Notice the app1 in here
    cmd = cleos() + ['push', 'action', 'app1', 'revoke', json.dumps(d), '-p',
                     'user1']
    ret = subprocess.check_output(cmd, universal_newlines=True)


def get_table():
    print('Getting table')
    d = {
        'user_account': 'user3',
        'requesting_app': 'app2'
    }
    # TODO: Notice the app1 in here
    cmd = cleos() + ['get', 'table', 'app1', 'app2', 'unifacl']
    ret = subprocess.check_output(cmd, universal_newlines=True)
    print(ret)


def process():
    create_users(usernames + appnames)

    keys = [create_key() for x in range(len(usernames + appnames))]

    for username, keys in zip(usernames + appnames, keys):
        wallet_import_key(username, keys[1])
        create_account(username, keys[0])

    for appname in appnames:
        associate_contracts(appname)

    mother_contract('unif.mother')

    for appname in appnames:
        # set_schema(appname)
        contract_hash = get_code_hash(appname)
        validate_with_mother(appname, contract_hash)

    grant_access()
    get_table()


def configure_logging():
    log.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    log.addHandler(ch)


if __name__ == "__main__":
    configure_logging()
    process()
