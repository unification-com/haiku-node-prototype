import json
import logging
import requests
import time

import click

from pathlib import Path

from haiku_node.keystore.keystore import UnificationKeystore
from haiku_node.validation.encryption import sign_request

password_config = Path('data/system.json')

contents = password_config.read_text()
password_d = json.loads(contents)

log = logging.getLogger(__name__)

print("System test where App2 makes a request to App1")


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


def systest_auth(protocol, host, port):
    base_url = f"{protocol}://{host}:{port}"
    body = 'request body'
    requesting_app = 'app2'
    password = password_d[requesting_app]['password']
    encoded_password = str.encode(password)
    ks = UnificationKeystore(encoded_password, app_name=requesting_app)

    private_key = ks.get_rpc_auth_private_key()

    signature = sign_request(private_key, body)
    broken_signature = 'unlucky' + signature[7:]

    payload = {"eos_account_name": requesting_app,
               "signature": broken_signature,
               "body": body}

    log.info('Making request')
    r = requests.post(f"{base_url}/data_request", json=payload, verify=False)

    assert r.status_code == 200
    assert r.json()['success'] is False

    payload = {"eos_account_name": requesting_app,
               "signature": signature,
               "body": body}

    r = requests.post(f"{base_url}/data_request", json=payload, verify=False)
    assert r.json()['success'] is True


@main.command()
def probe():
    """
    Run a few tests on a system that is already up
    """
    systest_auth('https', 'haiku-app1', 8050)


@main.command()
def host():
    """
    Test from the host machine
    """
    systest_auth('http', 'localhost', 5000)


@main.command()
def wait():
    """
    Wait for the system to come up
    """
    log.info('Waiting for the system to come up')

    # TODO: Implementing sleeping for now
    print("Sleeping")
    time.sleep(10)
    systest_auth('https', 'haiku-app1', 8050)
    systest_auth('https', 'haiku-app2', 8050)
    time.sleep(6000)


if __name__ == "__main__":
    main()
