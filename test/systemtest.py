import json
import logging
import time

from pathlib import Path

from eosapi import Client

import click
import requests

from haiku_node.blockchain_helpers.accounts import (
    AccountManager, make_default_accounts, create_public_data)
from haiku_node.blockchain.eos.mother import UnificationMother
from haiku_node.blockchain.eos.uapp import UnificationUapp
from haiku_node.blockchain.eos.und_rewards import UndRewards
from haiku_node.client import HaikuDataClient, Provider
from haiku_node.config.config import UnificationConfig
from haiku_node.encryption.merkle.merkle_tree import MerkleTree
from haiku_node.encryption.payload import bundle
from haiku_node.keystore.keystore import UnificationKeystore
from haiku_node.network.eos import (get_eos_rpc_client,
                                    get_cleos, get_ipfs_client)
from haiku_node.permissions.perm_batch_db import (
    default_db as pb_default_db, PermissionBatchDatabase)
from haiku_node.permissions.permissions import UnifPermissions

demo_config = json.loads(Path('data/demo_config.json').read_text())
password_d = demo_config["system"]

log = logging.getLogger('haiku_node')


def init_logging():
    log.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    log.addHandler(ch)


@click.group()
def main():
    init_logging()


def systest_auth(requesting_app, providing_app, user):
    """
    Ensuring that an incorrectly signed request is rejected.

    """
    def broken(d, field):
        d[field] = 'unlucky' + d[field][7:]
        return d

    log.info(f'{requesting_app} is requesting data from {providing_app}')

    body = {'users': [user], 'data_id': 'request_hash'}

    app_config = demo_config['demo_apps'][providing_app]
    port = app_config['rpc_server_port']

    eos_client = get_eos_rpc_client()
    mother = UnificationMother(eos_client, providing_app, get_cleos(),
                               get_ipfs_client())
    provider_obj = Provider(providing_app, 'https', mother)

    encoded_password = demo_config['system'][requesting_app]['password']

    ks = UnificationKeystore(encoded_password, app_name=requesting_app,
                             keystore_path=Path('data/keys'))
    payload = bundle(ks, requesting_app, provider_obj.name, body, 'Success')
    payload = broken(payload, 'signature')

    r = provider_obj.post('data_request', payload)
    assert r.status_code == 401


def systest_ingest(requesting_app, providing_app, user, balances):
    log.info(f'Testing Fetch ingestion: {requesting_app} '
             f'is requesting data from {providing_app}')
    request_hash = f'data-request-{providing_app}-{requesting_app}'

    app_config = demo_config['demo_apps'][providing_app]
    port = app_config['rpc_server_port']

    eos_client = get_eos_rpc_client()
    mother = UnificationMother(eos_client, providing_app, get_cleos(),
                               get_ipfs_client())
    provider_obj = Provider(providing_app, 'https', mother)

    password = demo_config['system'][requesting_app]['password']
    encoded_password = str.encode(password)
    keystore = UnificationKeystore(encoded_password, app_name=requesting_app,
                                   keystore_path=Path('data/keys'))

    conf = UnificationConfig()
    eos_client = Client(
        nodes=[f"http://{conf['eos_rpc_ip']}:{conf['eos_rpc_port']}"])
    consumer_uapp_sc = UnificationUapp(eos_client, requesting_app)

    price_sched = demo_config['demo_apps'][providing_app]['db_schemas'][0]['price_sched']

    latest_req_id = consumer_uapp_sc.init_data_request(provider_obj.name,
                                                       "0", "0",
                                                       price_sched)

    client = HaikuDataClient(keystore)
    client.make_data_request(requesting_app, provider_obj, user,
                             request_hash, latest_req_id)
    client.read_data_from_store(provider_obj, request_hash)

    # Update the system test record of the balances
    balances[requesting_app] = balances[requesting_app] - price_sched
    und_rewards = UndRewards(providing_app, price_sched)
    balances[providing_app] = (balances[providing_app]
                               + und_rewards.calculate_reward(is_user=False))

    return balances


def systest_accounts():
    log.info('Running systest accounts')

    demo_config = json.loads(Path('data/demo_config.json').read_text())
    appnames = ['app1', 'app2', 'app3']
    usernames = ['user1', 'user2', 'user3', 'unif.mother', 'unif.token']

    manager = AccountManager(host=False)
    make_default_accounts(manager, demo_config, appnames, usernames)

    work_dir = Path('data/public')
    create_public_data(manager, work_dir, appnames)


def systest_smart_contract_mother():
    log.info('Running systest smart contract MOTHER')
    d_conf = json.loads(Path('data/demo_config.json').read_text())
    appnames = ['app1', 'app2', 'app3']
    d_apps = d_conf['demo_apps']
    conf = UnificationConfig()
    eos_client = Client(
        nodes=[f"http://{conf['eos_rpc_ip']}:{conf['eos_rpc_port']}"])

    for appname in appnames:
        log.info("------------------------------------------")
        app_data = d_apps[appname]
        log.info(f"Contacting MOTHER for {app_data['eos_sc_account']}")
        mother = UnificationMother(
            eos_client, app_data['eos_sc_account'],
            get_cleos(), get_ipfs_client())

        log.info("App is Valid")
        log.info("Expecting: True")
        log.info(f"Actual - MOTHER: {mother.valid_app()}")
        assert mother.valid_app() is True

        log.info("App Code is Valid")
        log.info("Expecting: True")
        log.info(f"Actual - MOTHER: {mother.valid_code()}")
        assert mother.valid_app() is True

        log.info("Code Hash")
        log.info(
            f"Expecting - config.json: {mother.get_deployed_contract_hash()}")
        log.info(f"Actual - MOTHER: {mother.get_hash_in_mother()}")
        assert (mother.get_deployed_contract_hash()
                == mother.get_hash_in_mother()) is True

        log.info("RPC IP")
        log.info(f"Expecting - config.json: {app_data['rpc_server']}")
        log.info(f"Actual - MOTHER: {mother.get_haiku_rpc_ip()}")
        assert (app_data['rpc_server'] == mother.get_haiku_rpc_ip()) is True

        log.info("RPC Port")
        log.info(f"Expecting - config.json: {app_data['rpc_server_port']}")
        log.info(f"Actual - MOTHER: {mother.get_haiku_rpc_port()}")
        assert (int(app_data['rpc_server_port']) == int(
            mother.get_haiku_rpc_port())) is True

        log.info("------------------------------------------")


def systest_smart_contract_uapp():
    log.info('Running systest smart contract UApp')
    d_conf = json.loads(Path('data/demo_config.json').read_text())
    appnames = ['app1', 'app2', 'app3']
    d_apps = d_conf['demo_apps']

    conf = UnificationConfig()
    eos_client = Client(
        nodes=[f"http://{conf['eos_rpc_ip']}:{conf['eos_rpc_port']}"])

    for appname in appnames:
        log.info("------------------------------------------")
        app_data = d_apps[appname]
        conf_db_schemas = app_data['db_schemas']
        uapp_sc = UnificationUapp(eos_client, app_data['eos_sc_account'])
        log.info("Check DB Schemas are correctly configured")

        for schema_obj in conf_db_schemas:
            log.info(f"Check schema {schema_obj['schema_name']}")
            conf_schema = schema_obj['schema']
            log.info(f"Expecting - config.json: {conf_schema}")

            # version set to 1, since that's the hard coded version used in
            # accounts.validate_with_mother
            uapp_contract_schema = uapp_sc.get_db_schema_by_pkey(0)
            log.info(f"Actual - UApp Smart Contract: "
                     f"{uapp_contract_schema['schema']}")
            assert (conf_schema == uapp_contract_schema['schema']) is True


def systest_process_permission_batches():
    appnames = ['app1', 'app2', 'app3']

    for app_name in appnames:
        log.debug(f'run systest_process_permission_batches for {app_name}')
        mother = UnificationMother(get_eos_rpc_client(), app_name, get_cleos(),
                                   get_ipfs_client())
        provider_obj = Provider(app_name, 'https', mother)

        password = demo_config['system'][app_name]['password']
        encoded_password = str.encode(password)
        keystore = UnificationKeystore(encoded_password, app_name=app_name,
                                   keystore_path=Path('data/keys'))

        client = HaikuDataClient(keystore)
        try:
            client.process_permissions_batch(provider_obj)
        except Exception as e:
            log.error(f'systest_process_permission_batches failed: {e}')


def compile_actors():
    users = []
    consumers = []
    providers = []

    for user, app_permission_list in demo_config['demo_permissions'].items():
        if user not in users:
            users.append(user)
        for consumer, providers in app_permission_list.items():
            if consumer not in consumers:
                consumers.append(consumer)
            for provider, permissions in providers.items():
                if provider not in providers:
                    providers.append(provider)

    return users, consumers, providers


def systest_check_permission_requests():

    ipfs = get_ipfs_client()
    users, consumers, providers = compile_actors()

    for provider in providers:
        log.debug(f'run systest_check_permission_requests'
                  f' for Provider {provider}')

        provider_uapp = UnificationUapp(get_eos_rpc_client(), provider)

        permission_db = PermissionBatchDatabase(pb_default_db())
        permissions = UnifPermissions(ipfs, provider_uapp, permission_db)

        for consumer in consumers:
            if consumer != provider:
                log.debug(f'Provider {provider}: load permissions '
                          f'for Consumer {consumer}')
                permissions.load_consumer_perms(consumer)
                for user in users:
                    user_permissions = permissions.get_user_perms_for_all_schemas(user)
                    for schema_id, user_perms in user_permissions.items():
                        log.debug(f'User {user}, '
                                  f'Schema {schema_id}: {user_perms}')
                        is_valid = permissions.verify_permission(user_perms)
                        log.debug(f'Perm sig valid: {is_valid}')

                        assert is_valid

                        demo_conf_check = demo_config['demo_permissions'][user][consumer][provider]

                        demo_conf_fields = demo_conf_check['fields']
                        demo_conf_granted = demo_conf_check['granted']
                        demo_conf_schema_id = demo_conf_check['schema_id']

                        assert int(demo_conf_schema_id) == int(schema_id)

                        if demo_conf_granted:
                            log.debug("Permission granted")
                            log.debug(f"Demo fields: {demo_conf_fields}, "
                                      f"recorded fields: "
                                      f"{user_perms['perms']}")
                            assert demo_conf_fields == user_perms['perms']
                        else:
                            log.debug("Permission not granted. Recorded "
                                      "perms should be empty")
                            log.debug(f"Recorded fields: "
                                      f"{user_perms['perms']}")
                            assert user_perms['perms'] == ''


def systest_merkle_proof_permissions():
    ipfs = get_ipfs_client()
    users, consumers, providers = compile_actors()

    for provider in providers:
        log.debug(f'run systest_merkle_proof_'
                  f'permissions for Provider {provider}')

        provider_uapp = UnificationUapp(get_eos_rpc_client(), provider)

        permission_db = PermissionBatchDatabase(pb_default_db())
        permissions = UnifPermissions(ipfs, provider_uapp, permission_db)

        for consumer in consumers:
            if consumer != provider:
                log.debug(f'Provider {provider}: load '
                          f'permissions for Consumer {consumer}')
                permissions.load_consumer_perms(consumer)

                permissions_obj = permissions.get_all_perms()

                tree = MerkleTree()

                for user, perm in permissions_obj['permissions'].items():
                    for schema_id, schema_perm in perm.items():
                        tree.add_leaf(json.dumps(schema_perm))

                tree.grow_tree()

                log.debug(f"Generated merkle root: {tree.get_root_str()}")
                log.debug(f"Recorded merkle root: "
                          f"{permissions_obj['merkle_root']}")

                for user, perm in permissions_obj['permissions'].items():
                    for schema_id, schema_perm in perm.items():
                        requested_leaf = json.dumps(schema_perm)
                        proof_chain = tree.get_proof(requested_leaf,
                                                     is_hashed=False)
                        log.debug(f'Permission leaf for {user}:'
                                  f' {requested_leaf}')
                        log.debug(f'Proof chain for {user} - '
                                  f'Schema {schema_id} '
                                  f'permission leaf: '
                                  f'{json.dumps(proof_chain)}')

                        # simulate only having access to leaf,
                        # root and proof chain for leaf
                        verify_tree = MerkleTree()

                        is_good = verify_tree.verify_leaf(requested_leaf,
                                                          permissions_obj['merkle_root'],
                                                          proof_chain,
                                                          is_hashed=False)

                        log.debug(f'Leaf is valid: {is_good}')

                        assert is_good


def completion_banner():
    return '\n' \
           '==============================================\n' \
           '= HAIKU NODE PROTOTYPE INITIALISED AND READY =\n' \
           '= ------------------------------------------ =\n' \
           '= You can now interact with the demo         =\n' \
           '= system. Read the wiki for more details     =\n' \
           '= on how to interact with the demo           =\n' \
           '==============================================\n'


@main.command()
def wait():
    """
    Wait for the system to come up.
    """
    log.info('Waiting for the system to come up')

    time.sleep(5)

    # create EOS accounts
    log.info('Create EOS Accounts')
    systest_accounts()

    time.sleep(20)

    # Deploy and populate Smart Contracts
    log.info('Ensure accounts are created, and contracts populated')
    systest_smart_contract_mother()
    systest_smart_contract_uapp()

    systest_process_permission_batches()

    time.sleep(3)

    systest_check_permission_requests()
    systest_merkle_proof_permissions()

    manager = AccountManager(host=False)

    # First ensure that an incorrectly signed request is rejected
    log.info('run systest_auth')
    systest_auth('app1', 'app2', 'user1')

    balances = {}
    for k, d in demo_config['demo_apps'].items():
        balances[d['eos_sc_account']] = d['und_rewards']['start_balance']

    log.info('run systest_ingest')
    balances = systest_ingest('app1', 'app2', 'user1', balances)
    balances = systest_ingest('app2', 'app1', 'user1', balances)
    balances = systest_ingest('app3', 'app1', 'user1', balances)
    balances = systest_ingest('app3', 'app2', 'user2', balances)

    time.sleep(1)
    for app, balance in balances.items():
        log.info(f"App {app} has a balance of {balance} UND")
        assert manager.get_und_rewards(app) == balance

    # The User3 has denied access to for app2 to access data on app 1
    # balances = systest_ingest('app2', 'app1', 'user3', balances)
    # TODO: User denied requests have granular balance effects

    log.info(completion_banner())

    # Run forever, so that one can exec into the container
    while True:
        time.sleep(6000)


if __name__ == "__main__":
    main()
