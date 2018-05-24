import json
import tempfile
from pathlib import Path

import logging

import requests

from haiku_node.rpc import verify_account
from haiku_node.validation.encryption import sign_request, decrypt

log = logging.getLogger(__name__)


class HaikuDataClient:
    def __init__(self, keystore, protocol='https', local=False):
        self.keystore = keystore
        self.local = local
        self.protocol = protocol
        self.config = json.loads(Path('data/demo_config.json').read_text())

    def transform_request_id(self, request_hash):
        """
        # TODO: Convert to a particular request body
        """
        return request_hash

    def base_url(self, providing_app):
        app_config = self.config['demo_apps'][providing_app]
        if not self.local:
            host = app_config['rpc_server']
        else:
            host = '127.0.0.1'
        port = app_config['rpc_server_port']
        return f"{self.protocol}://{host}:{port}"

    def persist_data(self, providing_app, request_hash, data):
        temp_dir = Path(tempfile.gettempdir())

        tp = temp_dir / Path(f"{providing_app}-{request_hash}")
        log.info(f'Writing to {tp}')
        tp.write_text(data, encoding='utf-8')

    def make_data_request(self, requesting_app, providing_app, request_hash):
        """
        Make a data request from one App to another.
        """

        body = self.transform_request_id(request_hash)
        private_key = self.keystore.get_rpc_auth_private_key()

        signature = sign_request(private_key, body)

        payload = {"eos_account_name": requesting_app,
                   "signature": signature,
                   "body": body}

        base = self.base_url(providing_app)
        r = requests.post(f"{base}/data_request", json=payload, verify=False)
        d = r.json()

        # Now verify the response
        encrypted_body = d['body']
        decrypted_body = decrypt(private_key, encrypted_body)
        verify_account(providing_app, decrypted_body, d['signature'])

        log.info(f'"In the air" decrypted content is: {decrypted_body}')

        self.persist_data(providing_app, request_hash, encrypted_body)

    def read_data_from_store(self, providing_app, request_hash):
        temp_dir = Path(tempfile.gettempdir())

        tp = temp_dir / Path(f"{providing_app}-{request_hash}")
        encrypted_body = tp.read_text()

        private_key = self.keystore.get_rpc_auth_private_key()

        decrypted_body = decrypt(private_key, encrypted_body)
        log.info(f'Decrypted content from persistence store: {decrypted_body}')
        return decrypted_body
