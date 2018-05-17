import json
import subprocess
import logging

import requests

from eosapi import Client

log = logging.getLogger(__name__)


d = {
    "eos_rpc_ip": "127.0.0.1",
    "eos_rpc_port": "8888"
}

eosClient = Client(
    nodes=['http://' + d['eos_rpc_ip'] + ':' + d['eos_rpc_port']])


appnames = ['app1', 'app2', 'app3']
usernames = ['user1', 'user2', 'user3', 'unif.mother']
app_config = {}


def get_app_config():
    global app_config
    with open('data/test_apps.json') as f:
        app_config = json.load(f)


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
                     "/eos/contracts/unification_acl/unification_acl.wast",
                     "/eos/contracts/unification_acl/unification_acl.abi",
                     "-p", username]
    ret = subprocess.check_output(cmd, universal_newlines=True)
    print(ret)


def mother_contract(username):
    log.info('Associating mother contracts')
    cmd = cleos() + ["set", "contract", username,
                     "/eos/contracts/unification_mother",
                     "/eos/contracts/unification_mother/unification_mother.wast",
                     "/eos/contracts/unification_acl/unification_mother.abi",
                     "-p", username]
    ret = subprocess.check_output(cmd, universal_newlines=True)
    print(ret)


def set_schema(appname):
    app_conf = app_config[appname]
    for i in app_conf['db_schemas']:
        cmd = cleos() + ['push', 'action', appname, 'setschema',
                     f'{"schema_name":"{i["schema_name"]},"schema":"{i["schema"]}" }', '-p', appname]
        ret = subprocess.check_output(cmd, universal_newlines=True)
        print(ret)


def set_data_sources(appname):
    app_conf = app_config[appname]
    for i in app_conf['data_sources']:
        cmd = cleos() + ['push', 'action', appname, 'setsource',
                         f'{"source_name":"{i["source_name"]},"source_type":"{i["source_type"]}" }', '-p', appname]
        ret = subprocess.check_output(cmd, universal_newlines=True)
        print(ret)


def get_code_hash(appname):
    cmd = cleos() + ['get', 'code', appname]
    ret = subprocess.check_output(cmd, universal_newlines=True)
    return ret.strip()[len('code hash: '):]


def validate_with_mother(appname):
    # TODO: Fix the names

    contract_hash = get_code_hash(appname)

    app_conf = app_config[appname]
    schema_vers = ""
    for i in app_conf['db_schemas']:
        schema_vers = schema_vers + i['schema_name'] + ":1,"

    schema_vers = schema_vers.rstrip(",")

    d = {
        'acl_contract_acc': appname,
        'schema_vers': schema_vers,
        'acl_contract_hash': contract_hash,
        'rpc_server_ip': app_conf['rpc_server'],
        'rpc_server_port': app_conf['rpc_server_port']
    }
    cmd = cleos() + ['push', 'action', 'unif.mother', 'validate', json.dumps(d),
                     '-p', 'unif.mother']
    ret = subprocess.check_output(cmd, universal_newlines=True)


def set_permissions():
    print('Setting permissions')
    with open('data/test_permissions.json') as f:
        test_permissions = json.load(f)
        for user_perms in test_permissions:
            user = user_perms['user']
            for haiku in user_perms['haiku_nodes']:
                app = haiku['app']
                for req_app in haiku['req_apps']:
                    d = {
                        'user_account': user,
                        'requesting_app': req_app['account']
                    }
                    if req_app['granted']:
                        cmd = cleos() + ['push', 'action', app, 'grant', json.dumps(d), '-p', user]
                        ret = subprocess.check_output(cmd, universal_newlines=True)
                        print(ret)
                    else:
                        cmd = cleos() + ['push', 'action', app, 'revoke', json.dumps(d), '-p', user]
                        ret = subprocess.check_output(cmd, universal_newlines=True)
                        print(ret)


# def deny_access():
#     d = {
#         'user_account': 'user3',
#         'requesting_app': 'app2'
#     }
#     # TODO: Notice the app1 in here
#     cmd = cleos() + ['push', 'action', 'app1', 'revoke', json.dumps(d), '-p',
#                      'user1']
#     ret = subprocess.check_output(cmd, universal_newlines=True)


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
    get_app_config()

    create_users(usernames + appnames)

    keys = [create_key() for x in range(len(usernames + appnames))]

    for username, keys in zip(usernames + appnames, keys):
        wallet_import_key(username, keys[1])
        create_account(username, keys[0])

    mother_contract('unif.mother')

    for appname in appnames:
        associate_contracts(appname)
        set_schema(appname)
        set_data_sources(appname)
        validate_with_mother(appname)

    set_permissions()
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
