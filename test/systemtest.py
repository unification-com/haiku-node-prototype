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

password_config = Path('data/system.json')

contents = password_config.read_text()
password_d = json.loads(contents)

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

    from haiku_node.eosio_helpers.accounts import AccountManager, \
        make_default_accounts

    app_config = json.loads(Path('data/test_apps.json').read_text())
    demo_config = json.loads(Path('data/demo_config.json').read_text())
    appnames = ['app1', 'app2', 'app3']
    usernames = ['user1', 'user2', 'user3', 'unif.mother']

    manager = AccountManager(host=False)
    make_default_accounts(manager, app_config, demo_config, appnames, usernames)


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

    time.sleep(6000)


if __name__ == "__main__":
    main()
