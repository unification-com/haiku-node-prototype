import json
import tempfile
import xml.etree.ElementTree as etree
from pathlib import Path

import logging
import requests

from haiku_node.encryption.payload import bundle, unbundle
from haiku_node.blockchain.und_rewards import UndRewards

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

        # TODO: only pay if data is valid
        und_reward = UndRewards()

        tree = etree.ElementTree(etree.fromstring(decrypted_body))
        users_to_pay = tree.findall('unification_users/unification_user')
        for username in users_to_pay:
            print(f'pay {username.text}')
            ret = und_reward.send_reward(username.text)
            print(ret)

        print(f"Pay provider {providing_app.name}")
        ret = und_reward.send_reward(providing_app.name, False)
        print(ret)

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

