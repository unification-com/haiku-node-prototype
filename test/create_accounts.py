import os, inspect
import json
import logging
import subprocess
import sqlite3

import requests

from pathlib import Path

from haiku_node.blockchain.acl import UnificationACL
from haiku_node.blockchain.mother import UnificationMother

log = logging.getLogger(__name__)

d = {
    "eos_rpc_ip": "127.0.0.1",
    "eos_rpc_port": "8888"
}


appnames = ['app1', 'app2', 'app3']
usernames = ['user1', 'user2', 'user3', 'unif.mother']
currentdir = os.path.dirname(
            os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)

demo_config = json.loads(Path(parentdir + '/test/data/demo_config.json').read_text())

demo_apps = demo_config['demo_apps']
demo_permissions = demo_config['demo_permissions']


def base_url():
    return f"http://{d['eos_rpc_ip']}:{d['eos_rpc_port']}"


def keos_url():
    keos_ip = '127.0.0.1'
    keos_port = 8889
    return f"http://{keos_ip}:{keos_port}"


def create_user(username):
    url = f"{keos_url()}/v1/wallet/create"
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
    url = f"{keos_url()}/v1/wallet/unlock"
    r = requests.post(url, data=serialise([username, password]))


def cleos():
    return ["/usr/local/bin/docker", "exec", "docker_keosd_1",
            "/opt/eosio/bin/cleos", "--url", "http://nodeosd:8888",
            "--wallet-url", "http://localhost:8889"]


def delete_wallet_files():
    log.info('Deleting wallets on the keos node')
    cmd = ["/usr/local/bin/docker", "exec", "docker_keosd_1", "/bin/bash",
           '-c', 'rm -f /opt/eosio/bin/data-dir/*.wallet']
    subprocess.check_output(cmd, universal_newlines=True)


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
    subprocess.check_output(cmd, universal_newlines=True)


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
                     "/eos/contracts/unification_mother/unification_mother.abi",
                     "-p", username]

    ret = subprocess.check_output(cmd, universal_newlines=True)
    print(ret)


def set_schema(appname):
    log.info('Set Schemas')
    app_conf = demo_apps[appname]
    for i in app_conf['db_schemas']:
        d = {
            'schema_name': i['schema_name'],
            'schema': i['schema'],
        }
        cmd = cleos() + ['push', 'action', appname, 'setschema',
                         json.dumps(d), '-p', appname]
        subprocess.check_output(cmd, universal_newlines=True)


def set_data_sources(appname):
    log.info('Set Data sources')
    app_conf = demo_apps[appname]
    for i in app_conf['data_sources']:
        d = {
            'source_name': i['source_name'],
            'source_type': i['source_type'],
        }

        cmd = cleos() + ['push', 'action', appname, 'setsource', json.dumps(d),
               '-p', appname]
        ret = subprocess.check_output(cmd, universal_newlines=True)
        print(ret)


def get_code_hash(appname):
    cmd = cleos() + ['get', 'code', appname]
    ret = subprocess.check_output(cmd, universal_newlines=True)
    return ret.strip()[len('code hash: '):]


def validate_with_mother(appname):
    # TODO: Fix the names

    log.info('Validate with MOTHER')
    contract_hash = get_code_hash(appname)

    app_conf = demo_apps[appname]
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
    global demo_permissions

    for user_perms in demo_permissions['permissions']:
        user = user_perms['user']
        for haiku in user_perms['haiku_nodes']:
            app = haiku['app']
            for req_app in haiku['req_apps']:
                d = {
                    'user_account': user,
                    'requesting_app': req_app['account']
                }
                if req_app['granted']:
                    cmd = cleos() + ['push', 'action', app, 'grant',
                                     json.dumps(d), '-p', user]
                    ret = subprocess.check_output(cmd,
                                                  universal_newlines=True)
                    print(ret)
                else:
                    cmd = cleos() + ['push', 'action', app, 'revoke',
                                     json.dumps(d), '-p', user]
                    ret = subprocess.check_output(cmd,
                                                  universal_newlines=True)
                    print(ret)


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


def run_test_mother(app):
    print("Contacting MOTHER FOR: ", app)

    um = UnificationMother(d['eos_rpc_ip'], d['eos_rpc_port'], app)
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


def run_test_acl(app):
    print("Loading ACL/Meta Contract for: ", app)

    u_acl = UnificationACL(d['eos_rpc_ip'], d['eos_rpc_port'], app)

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


def create_lookup_db(app):
    global demo_apps
    app_conf = demo_apps[app]

    log.info(f'Create {app} Lookup database')
    currentdir = os.path.dirname(
        os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    db_path = Path(f'{parentdir}/test/data/{app}_unification_lookup.db')
    db_name = str(db_path.resolve())

    log.info(db_name)

    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute('''CREATE TABLE lookup
                             (native_id text, eos_account text)''')

    c.execute('''CREATE TABLE lookup_meta
                                     (native_table text, native_field text, field_type text)''')

    c.execute('''CREATE TABLE schema_map
                                         (sc_schema_name text, native_db text, native_db_platform text)''')

    c.execute(f"INSERT INTO lookup_meta VALUES ('{app_conf['lookup']['lookup_meta']['native_table']}', "
              f"'{app_conf['lookup']['lookup_meta']['native_field']}', "
              f"'{app_conf['lookup']['lookup_meta']['field_type']}')")

    for u in app_conf['lookup']['lookup_users']:
        c.execute(f"INSERT INTO lookup VALUES ('{u['native_id']}', '{u['eos_account']}')")

    for sc in app_conf['db_schemas']:
        c.execute(f"INSERT INTO schema_map VALUES ('{sc['schema_name']}', '{sc['database']}', '{sc['db_platform']}')")

    conn.commit()
    conn.close()

    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    log.info('check user2 == 2')
    t = ('user2',)
    c.execute('SELECT native_id FROM lookup WHERE eos_account=?', t)
    res = c.fetchone()[0]
    print("user2 native ID:", res)

    conn.close()


def process():
    delete_wallet_files()

    for username in usernames + appnames:
        password = create_user(username)
        print(f"User {username} with password {password}")

        unlock_wallet(username, password)
        print(f"Wallet unlocked")

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
        create_lookup_db(appname)

    set_permissions()
    #get_table()
    for appname in appnames:
        print(f'==========RUN CONTRACT TESTS FOR {appname}==========')
        run_test_mother(appname)
        run_test_acl(appname)
        print(f'==========END CONTRACT TESTS FOR {appname}==========')


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
