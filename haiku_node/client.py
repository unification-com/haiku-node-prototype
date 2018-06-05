import json
import tempfile
from pathlib import Path

import logging

import requests

from haiku_node.validation.payload import bundle, unbundle

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

    def persist_data(self, providing_app_name: str, request_hash, data: dict):
        temp_dir = Path(tempfile.gettempdir())

        tp = temp_dir / Path(f"{providing_app_name}-{request_hash}")
        log.info(f'Writing to {tp}')
        tp.write_text(json.dumps(data), encoding='utf-8')
        return tp

    def make_data_request(
            self, requesting_app, providing_app: Provider, user, request_hash):
        """
        Make a data request from one App to another.
        """

        body = self.transform_request_id(user, request_hash)
        payload = bundle(requesting_app, providing_app.name, body, 'Success')

        base = providing_app.base_url()
        r = requests.post(f"{base}/data_request", json=payload, verify=False)
        d = r.json()

        if r.status_code == 401:
            raise Unauthorized(d['message'])
        if r.status_code != 200:
            raise Exception(d['message'])

        bundle_d = unbundle(providing_app.name, requesting_app, d)
        decrypted_body = bundle_d['data']

        log.info(f'"In the air" decrypted content is: {decrypted_body}')

        return self.persist_data(
            providing_app.name, request_hash, d)

    def read_data_from_store(
            self, providing_app: Provider, requesting_app, request_hash):
        temp_dir = Path(tempfile.gettempdir())

        tp = temp_dir / Path(f"{providing_app.name}-{request_hash}")
        encrypted_body = tp.read_text()

        d = json.loads(encrypted_body)

        bundle_d = unbundle(providing_app.name, requesting_app, d)
        decrypted_body = bundle_d['data']

        log.info(f'Decrypted content from persistence store: {decrypted_body}')
        return decrypted_body
