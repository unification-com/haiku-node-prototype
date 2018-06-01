import json
import tempfile
from pathlib import Path

import logging

import requests

from haiku_node.rpc import verify_account
from haiku_node.validation.encryption import sign_request, decrypt

log = logging.getLogger(__name__)


class Provider:
    def __init__(self, name, protocol, host, port):
        self.name = name
        self.protocol = protocol
        self.host = host
        self.port = port

    def base_url(self):
        return f"{self.protocol}://{self.host}:{self.port}"


class Unauthorized(Exception):
    pass


class HaikuDataClient:
    def __init__(self, keystore, protocol='https', local=False):
        self.keystore = keystore
        self.local = local
        self.protocol = protocol

    def transform_request_id(self, user, request_hash):
        """
        # TODO: Convert to a particular request body
        """
        return {
            'users': [user],
            'data_id': request_hash
        }

    def persist_data(self, providing_app_name: str, request_hash, data):
        temp_dir = Path(tempfile.gettempdir())

        tp = temp_dir / Path(f"{providing_app_name}-{request_hash}")
        log.info(f'Writing to {tp}')
        tp.write_text(data, encoding='utf-8')
        return tp

    def make_data_request(
            self, requesting_app, providing_app: Provider, user, request_hash):
        """
        Make a data request from one App to another.
        """

        body = self.transform_request_id(user, request_hash)
        private_key = self.keystore.get_rpc_auth_private_key()

        signature = sign_request(private_key, json.dumps(body))

        payload = {"eos_account_name": requesting_app,
                   "signature": signature,
                   "body": body}

        base = providing_app.base_url()
        r = requests.post(f"{base}/data_request", json=payload, verify=False)
        d = r.json()

        if r.status_code == 401:
            raise Unauthorized(d['message'])
        if r.status_code != 200:
            raise Exception(d['message'])

        # Now verify the response
        encrypted_body = d['body']
        decrypted_body = decrypt(private_key, encrypted_body)
        verify_account(providing_app.name, decrypted_body, d['signature'])

        log.info(f'"In the air" decrypted content is: {decrypted_body}')

        return self.persist_data(
            providing_app.name, request_hash, encrypted_body)

    def read_data_from_store(self, providing_app: Provider, request_hash):
        temp_dir = Path(tempfile.gettempdir())

        tp = temp_dir / Path(f"{providing_app.name}-{request_hash}")
        encrypted_body = tp.read_text()

        private_key = self.keystore.get_rpc_auth_private_key()

        decrypted_body = decrypt(private_key, encrypted_body)
        log.info(f'Decrypted content from persistence store: {decrypted_body}')
        return decrypted_body
