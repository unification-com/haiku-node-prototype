import json
import logging
import time

from pathlib import Path

import click
import requests

from haiku_node.config.keys import get_public_key
from haiku_node.rpc import verify_account
from haiku_node.keystore.keystore import UnificationKeystore
from haiku_node.validation.encryption import sign_request, decrypt, encrypt
from haiku_node.blockchain.mother import UnificationMother
from haiku_node.blockchain.acl import UnificationACL
from haiku_node.eosio_helpers import eosio_account

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


def systest_auth(base):
    """
    Testing signing and verifying a data request.

    App2 is requesting data from App1.
    """
    body = 'request body'
    requesting_app = 'app2'

    password = password_d[requesting_app]['password']
    encoded_password = str.encode(password)
    ks = UnificationKeystore(encoded_password, app_name=requesting_app)
    private_key = ks.get_rpc_auth_private_key()

    signature = sign_request(private_key, body)

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
    verify_account('app1', decrypted_body, d['signature'])


def systest_ingest(base):
    """
    App2 provides data for App1 to ingest.
    """
    body = 'ingestion body'
    requesting_app = 'app2'
    ingesting_app = 'app1'

    password = password_d[requesting_app]['password']
    encoded_password = str.encode(password)
    ks = UnificationKeystore(encoded_password, app_name=requesting_app)
    private_key = ks.get_rpc_auth_private_key()

    signature = sign_request(private_key, body)
    encrypted_body = encrypt(get_public_key(ingesting_app), body)

    payload = {"eos_account_name": requesting_app,
               "signature": signature,
               "body": encrypted_body}

    r = requests.post(f"{base}/data_ingest", json=payload, verify=False)
    assert r.status_code == 200
    d = r.json()
    assert d['success'] is True

    # Now verify the response
    verify_account('app1', d['body'], d['signature'])


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

    for appname in appnames:
        log.info("------------------------------------------")
        app_data = d_apps[appname]
        log.info(f"Contacting MOTHER for {app_data['eos_sc_account']}")
        mother = UnificationMother('nodeosd', 8888, app_data['eos_sc_account'])
        acl = UnificationACL('nodeosd', 8888, app_data['eos_sc_account'])

        log.info("App is Valid")
        log.info("Expecting: True")
        log.info(f"Actual - MOTHER: {mother.valid_app()}")
        assert mother.valid_app() is True

        log.info("App Code is Valid")
        log.info("Expecting: True")
        log.info(f"Actual - MOTHER: {mother.valid_code()}")
        assert mother.valid_app() is True

        log.info("Code Hash")
        log.info(f"Expecting - config.json: {mother.get_deployed_contract_hash()}")
        log.info(f"Actual - MOTHER: {mother.get_hash_in_mother()}")
        assert (mother.get_deployed_contract_hash() == mother.get_hash_in_mother()) is True

        log.info("RPC IP")
        log.info(f"Expecting - config.json: {app_data['rpc_server']}")
        log.info(f"Actual - MOTHER: {mother.get_haiku_rpc_ip()}")
        assert (app_data['rpc_server'] == mother.get_haiku_rpc_ip()) is True

        log.info("RPC Port")
        log.info(f"Expecting - config.json: {app_data['rpc_server_port']}")
        log.info(f"Actual - MOTHER: {mother.get_haiku_rpc_port()}")
        assert (int(app_data['rpc_server_port']) == int(mother.get_haiku_rpc_port())) is True

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

    for appname in appnames:
        log.info("------------------------------------------")
        app_data = d_apps[appname]
        conf_db_schemas = app_data['db_schemas']
        acl = UnificationACL('nodeosd', 8888, app_data['eos_sc_account'])
        log.info("Check DB Schemas are correctly configured")

        for schema_obj in conf_db_schemas:
            log.info(f"Check schema {schema_obj['schema_name']}")
            conf_schema = schema_obj['schema']
            log.info(f"Expecting - config.json: {conf_schema}")

            # version set to 1, since that's the hard coded version used in accounts.validate_with_mother
            acl_contract_schema = acl.get_current_valid_schema(schema_obj['schema_name'], 1)
            log.info(f"Actual - ACL/Meta Data Smart Contract: "
                     f"{acl_contract_schema['schema']}")
            assert (conf_schema == acl_contract_schema['schema']) is True


def systest_user_permissions():
    log.info('Running systest user permissions')
    d_conf = json.loads(Path('data/demo_config.json').read_text())
    demo_permissions = d_conf['demo_permissions']

    for user_perms in demo_permissions['permissions']:
        user = user_perms['user']
        user_acc_uint64 = eosio_account.string_to_name(user)

        for haiku in user_perms['haiku_nodes']:
            app = haiku['app']
            acl = UnificationACL('nodeosd', 8888, app)
            for req_app in haiku['req_apps']:
                log.info(f"Check {user} permissions granted for {req_app} in {app}")
                config_granted = req_app['granted']
                acl_granted, acl_revoked = acl.get_perms_for_req_app(req_app['account'])
                acl_perm = False
                if user_acc_uint64 in acl_granted:
                    acl_perm = True
                elif user_acc_uint64 in acl_revoked:
                    acl_perm = False

                log.info(f"Expecting - config.json: {config_granted}")
                log.info(f"Actual - ACL/Meta Data Smart Contract: {acl_perm}")

                assert (config_granted == acl_perm) is True


@main.command()
def probe():
    """
    Run a few tests on a system that is already up.
    """
    url_base = base_url('https', 'haiku-app1', 8050)
    systest_auth(url_base)
    systest_ingest(url_base)


@main.command()
def host():
    """
    Test from the host machine.
    """
    url_base = base_url('http', 'localhost', 8050)
    systest_auth(url_base)
    systest_ingest(url_base)


@main.command()
def wait():
    """
    Wait for the system to come up.
    """
    log.info('Waiting for the system to come up')

    # TODO: Implementing sleeping for now
    print("Sleeping")
    time.sleep(5)

    url_base = base_url('https', 'haiku-app1', 8050)
    systest_auth(url_base)
    systest_ingest(url_base)

    url_base = base_url('https', 'haiku-app2', 8050)
    systest_auth(url_base)
    systest_ingest(url_base)

    systest_accounts()

    log.info('Ensure accounts are created, and contracts populated')
    systest_smart_contract_mother()
    systest_smart_contract_acl()
    systest_user_permissions()

    time.sleep(6000)


if __name__ == "__main__":
    main()
