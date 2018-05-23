import json
import tempfile
from pathlib import Path

import logging

import requests

from haiku_node.keystore.keystore import UnificationKeystore
from haiku_node.rpc import verify_account
from haiku_node.validation.encryption import sign_request, decrypt

log = logging.getLogger(__name__)


class HaikuDataClient:
    def __init__(self, protocol='https', local=False):
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

    def persist_data(self, request_hash, data):
        temp_dir = Path(tempfile.gettempdir())

        tp = temp_dir / Path(request_hash)
        log.info(f'Writing to {tp}')
        tp.write_text(data, encoding='utf-8')

    def make_data_request(self, requesting_app, providing_app, request_hash):
        """
        Make a data request from one App to another.
        """

        body = self.transform_request_id(request_hash)

        password = self.config['system'][requesting_app]['password']
        encoded_password = str.encode(password)
        ks = UnificationKeystore(encoded_password, app_name=requesting_app)
        private_key = ks.get_rpc_auth_private_key()

        signature = sign_request(private_key, body)

        payload = {"eos_account_name": requesting_app,
                   "signature": signature,
                   "body": body}

        base = self.base_url(providing_app)
        r = requests.post(f"{base}/data_request", json=payload, verify=False)
        d = r.json()

        # Now verify the response
        decrypted_body = decrypt(private_key, d['body'])
        verify_account(providing_app, decrypted_body, d['signature'])

        self.persist_data(request_hash, decrypted_body)
