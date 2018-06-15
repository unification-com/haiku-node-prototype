import json
import logging
import time

from pathlib import Path

from eosapi import Client

import click
import requests

from haiku_node.blockchain.mother import UnificationMother
from haiku_node.blockchain.acl import UnificationACL
from haiku_node.client import HaikuDataClient, Provider
from haiku_node.config.config import UnificationConfig
from haiku_node.encryption.payload import bundle
from haiku_node.eosio_helpers import eosio_account
from haiku_node.eosio_helpers.accounts import (
    AccountManager, make_default_accounts)
from haiku_node.keystore.keystore import UnificationKeystore

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

    provider = Provider(
        providing_app, 'https', app_config['rpc_server'], port)

    payload = bundle(requesting_app, provider.name, body, 'Success')
    payload = broken(payload, 'signature')

    base = provider.base_url()

    r = requests.post(f"{base}/data_request", json=payload, verify=False)
    assert r.status_code == 401


def systest_ingest(requesting_app, providing_app, user, balances, local=False):
    log.info(f'Testing ingestion: {requesting_app} is requesting data from '
             f'{providing_app}')
    request_hash = f'data-request-{providing_app}-{requesting_app}'

    app_config = demo_config['demo_apps'][providing_app]
    port = app_config['rpc_server_port']
    if not local:
        provider = Provider(
            providing_app, 'https', app_config['rpc_server'], port)
    else:
        provider = Provider(providing_app, 'http', '127.0.0.1', port)

    password = demo_config['system'][requesting_app]['password']
    encoded_password = str.encode(password)
    keystore = UnificationKeystore(encoded_password, app_name=requesting_app)

    client = HaikuDataClient(keystore)
    client.make_data_request(requesting_app, provider, user, request_hash)
    client.read_data_from_store(provider, requesting_app, request_hash)

    # Update the system test record of the balances
    rewards = lambda app: demo_config['demo_apps'][app]['und_rewards']
    balances[requesting_app] = balances[requesting_app] - (
            rewards(requesting_app)['app_amt'] +
            rewards(requesting_app)['user_amt'])
    balances[providing_app] = (
            balances[providing_app] + rewards(requesting_app)['app_amt'])
    return balances


def systest_accounts():
    log.info('Running systest accounts')

    demo_config = json.loads(Path('data/demo_config.json').read_text())
    appnames = ['app1', 'app2', 'app3']
    usernames = ['user1', 'user2', 'user3', 'unif.mother', 'unif.token']

    manager = AccountManager(host=False)
    make_default_accounts(manager, demo_config, appnames, usernames)


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
        mother = UnificationMother(eos_client, app_data['eos_sc_account'])

        acl = UnificationACL(eos_client, app_data['eos_sc_account'])

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
        assert (mother.get_deployed_contract_hash() == mother.get_hash_in_mother()) is True

        log.info("RPC IP")
        log.info(f"Expecting - config.json: {app_data['rpc_server']}")
        log.info(f"Actual - MOTHER: {mother.get_haiku_rpc_ip()}")
        assert (app_data['rpc_server'] == mother.get_haiku_rpc_ip()) is True

        log.info("RPC Port")
        log.info(f"Expecting - config.json: {app_data['rpc_server_port']}")
        log.info(f"Actual - MOTHER: {mother.get_haiku_rpc_port()}")
        assert (int(app_data['rpc_server_port']) == int(
            mother.get_haiku_rpc_port())) is True

        log.info("Valid DB Schemas exist in ACL/Meta Smart Contract")
        valid_schemas = mother.get_valid_db_schemas()
        for sch_n, vers in valid_schemas.items():
            log.info(f'Schema {sch_n} version {vers}')
            schema = acl.get_current_valid_schema(sch_n, vers)
            log.info(schema)
            assert schema is not False

        log.info("------------------------------------------")


def systest_smart_contract_acl():
    log.info('Running systest smart contract ACL/Meta Data')
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
        acl = UnificationACL(eos_client, app_data['eos_sc_account'])
        log.info("Check DB Schemas are correctly configured")

        for schema_obj in conf_db_schemas:
            log.info(f"Check schema {schema_obj['schema_name']}")
            conf_schema = schema_obj['schema']
            log.info(f"Expecting - config.json: {conf_schema}")

            # version set to 1, since that's the hard coded version used in
            # accounts.validate_with_mother
            acl_contract_schema = acl.get_current_valid_schema(
                schema_obj['schema_name'], 1)
            log.info(f"Actual - ACL/Meta Data Smart Contract: "
                     f"{acl_contract_schema['schema']}")
            assert (conf_schema == acl_contract_schema['schema']) is True


def systest_user_permissions():
    log.info('Running systest user permissions')
    d_conf = json.loads(Path('data/demo_config.json').read_text())
    demo_permissions = d_conf['demo_permissions']
    conf = UnificationConfig()
    eos_client = Client(
        nodes=[f"http://{conf['eos_rpc_ip']}:{conf['eos_rpc_port']}"])

    for user_perms in demo_permissions['permissions']:
        user = user_perms['user']
        user_acc_uint64 = eosio_account.string_to_name(user)

        for haiku in user_perms['haiku_nodes']:
            app = haiku['app']
            acl = UnificationACL(eos_client, app)
            for req_app in haiku['req_apps']:
                log.info(
                    f"Check {user} permissions granted for {req_app} in {app}")
                config_granted = req_app['granted']
                acl_granted, acl_revoked = acl.get_perms_for_req_app(
                    req_app['account'])
                acl_perm = False
                if user_acc_uint64 in acl_granted:
                    acl_perm = True
                elif user_acc_uint64 in acl_revoked:
                    acl_perm = False

                log.info(f"Expecting - config.json: {config_granted}")
                log.info(f"Actual - ACL/Meta Data Smart Contract: {acl_perm}")

                assert (config_granted == acl_perm) is True


@main.command()
def host():
    """
    Test from the host machine.
    """
    balances = {}
    for k, d in demo_config['demo_apps'].items():
        balances[d['eos_sc_account']] = d['und_rewards']['start_balance']

    systest_ingest('app2', 'app1', 'user3', balances, local=True)


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
    systest_accounts()

    # Deploy and populate Smart Contracts
    log.info('Ensure accounts are created, and contracts populated')
    systest_smart_contract_mother()
    systest_smart_contract_acl()
    systest_user_permissions()

    time.sleep(20)

    manager = AccountManager(host=False)

    # First ensure that an incorrectly signed request is rejected
    systest_auth('app1', 'app2', 'user1')

    balances = {}
    for k, d in demo_config['demo_apps'].items():
        balances[d['eos_sc_account']] = d['und_rewards']['start_balance']

    balances = systest_ingest('app1', 'app2', 'user1', balances)
    balances = systest_ingest('app2', 'app1', 'user1', balances)
    balances = systest_ingest('app3', 'app1', 'user1', balances)
    balances = systest_ingest('app3', 'app2', 'user2', balances)

    time.sleep(1)
    for app, balance in balances.items():
        log.info(f"App {app} has a balance of {balance} UND")
        assert manager.get_und_rewards(app) == balance

    # The User3 has denied access to for app2 to access data on app 1
    balances = systest_ingest('app2', 'app1', 'user3', balances)
    # TODO: User denied requests have granular balance effects

    log.info(completion_banner())

    # Run forever, so that one can exec into the container
    while True:
        time.sleep(6000)


if __name__ == "__main__":
    main()
