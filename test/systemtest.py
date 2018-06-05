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
from haiku_node.eosio_helpers import eosio_account
from haiku_node.keystore.keystore import UnificationKeystore
from haiku_node.rpc import verify_account
from haiku_node.encryption.encryption import sign_request

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


def base_url(protocol, host, port):
    return f"{protocol}://{host}:{port}"


def systest_auth(requesting_app, providing_app, user):
    """
    Testing signing and verifying a data request.

    """
    log.info(f'{requesting_app} is requesting data from {providing_app}')

    base = base_url('https', f"haiku-{providing_app}", 8050)
    body = {
        'users': [user],
        'data_id': 'data-request'
    }

    password = password_d[requesting_app]['password']
    encoded_password = str.encode(password)
    ks = UnificationKeystore(encoded_password, app_name=requesting_app)
    private_key = ks.get_rpc_auth_private_key()

    signature = sign_request(private_key, json.dumps(body))

    # An unsuccessfully query
    broken_signature = 'unlucky' + signature[7:]
    payload = {"eos_account_name": requesting_app,
               "signature": broken_signature,
               "body": body}

    r = requests.post(f"{base}/data_request", json=payload, verify=False)

    assert r.status_code == 401
    assert r.json()['success'] is False

    # Now, a successful query
    payload = {"eos_account_name": requesting_app,
               "signature": signature,
               "body": body}

    r = requests.post(f"{base}/data_request", json=payload, verify=False)
    assert r.status_code == 200
    d = r.json()
    assert d['success'] is True

    # Now verify the response
    decrypted_body = decrypt(private_key, d['body'])
    verify_account(providing_app, decrypted_body, d['signature'])


def systest_ingest(requesting_app, providing_app, user, local=False):
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


def systest_accounts():
    log.info('Running systest accounts')

    from haiku_node.eosio_helpers.accounts import (
        AccountManager, make_default_accounts)

    demo_config = json.loads(Path('data/demo_config.json').read_text())
    appnames = ['app1', 'app2', 'app3']
    usernames = ['user1', 'user2', 'user3', 'unif.mother']

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
    systest_ingest('app2', 'app1', 'user3', local=True)


@main.command()
def wait():
    """
    Wait for the system to come up.
    """
    log.info('Waiting for the system to come up')

    print("Sleeping")
    time.sleep(5)

    # create EOS accounts
    systest_accounts()

    # Deploy and populate Smart Contracts
    log.info('Ensure accounts are created, and contracts populated')
    systest_smart_contract_mother()
    systest_smart_contract_acl()
    systest_user_permissions()

    # TODO: Implementing sleeping for now
    print("Sleeping")
    time.sleep(20)

    systest_ingest('app1', 'app2', 'user1')
    systest_ingest('app2', 'app1', 'user1')
    systest_ingest('app3', 'app1', 'user1')
    systest_ingest('app3', 'app2', 'user2')

    # The User3 has denied access to for app2 to access data on app 1
    try:
        systest_ingest('app2', 'app1', 'user3')
        assert False
    except Exception as e:
        assert True

    # Run forever
    while True:
        time.sleep(6000)


if __name__ == "__main__":
    main()
