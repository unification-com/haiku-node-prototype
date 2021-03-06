import hashlib
import json
import logging
import tempfile

from pathlib import Path

import requests

from haiku_node.blockchain.eos.mother import UnificationMother
from haiku_node.blockchain.eos.uapp import UnificationUapp
from haiku_node.blockchain.eos.und_rewards import UndRewards
from haiku_node.config.config import UnificationConfig
from haiku_node.encryption.payload import bundle, unbundle
from haiku_node.network.eos import get_eos_rpc_client, get_enum, Environment
from haiku_node.validation.validation import UnificationAppScValidation

log = logging.getLogger(__name__)


class Provider:
    def __init__(self, name: str, protocol: str, mother: UnificationMother):
        self.name = name
        self.protocol = protocol
        self.host = mother.get_haiku_rpc_ip()
        self.port = mother.get_haiku_rpc_port()

    def base_url(self):
        haiku_env = get_enum()
        if haiku_env == Environment.HOST:
            return f"https://localhost:8852"
        else:
            return f"{self.protocol}://{self.host}:{self.port}"

    def post(self, segment: str, payload):
        base = self.base_url()
        return requests.post(f"{base}/{segment}", json=payload, verify=False)

    def get(self, segment: str):
        base = self.base_url()
        return requests.get(f"{base}/{segment}", verify=False)

    def __repr__(self):
        return self.base_url()


class HaikuDataClient:
    def __init__(self, keystore, protocol='https', local=False):
        self.keystore = keystore
        self.local = local
        self.protocol = protocol

    def transform_request_id(self, user, request_hash, request_id=None):
        """
        # TODO: Convert to a particular request body
        """
        return {
            'users': [] if user is None else [user],
            'data_id': request_hash,
            'request_id': request_id
        }

    def persist_data(self, providing_app_name: str, request_hash, data: dict):
        temp_dir = Path(tempfile.gettempdir())

        tp = temp_dir / Path(f"{providing_app_name}-{request_hash}")
        log.info(f'Writing to {tp}')
        tp.write_text(json.dumps(data), encoding='utf-8')
        return tp

    def make_data_request(self, requesting_app, providing_app: Provider, user,
                          request_hash, request_id):
        # Check if the providing app is valid according to MOTHER
        eos_client = get_eos_rpc_client()
        v = UnificationAppScValidation(
            eos_client, providing_app.name)

        if not v.valid():
            raise Exception(f"Providing App {providing_app.name} is "
                            f"NOT valid according to MOTHER")

        body = self.transform_request_id(user, request_hash, request_id)
        payload = bundle(
            self.keystore, requesting_app, providing_app.name, body, 'Success')

        r = providing_app.post('data_request', payload)
        d = r.json()

        if r.status_code != 200:
            raise Exception(d['message'])

        bundle_d = unbundle(self.keystore, providing_app.name, d)
        decrypted_body = bundle_d['data']

        # log.info(f'"In the air" decrypted content is: {decrypted_body}')

        checksum_ok = False

        # Computationally validate the received data the checksum of the payload
        data_hash = hashlib.sha224(
            str(d['payload']).encode('utf-8')).hexdigest()

        uapp_sc = UnificationUapp(eos_client, requesting_app)
        data_request = uapp_sc.get_data_request_by_pkey(request_id)
        und_reward = UndRewards(requesting_app, data_request['price'])
        if data_request['hash'] == data_hash:
            print("Data computationally valid")
            checksum_ok = True

        json_obj = json.loads(decrypted_body)

        if 'no-data' not in json_obj and checksum_ok:
            users_to_pay = json_obj['unification_users']
            print("users_to_pay")
            print(users_to_pay)
            num_users = len(users_to_pay)
            print(f"Pay {num_users} users")

            for username in users_to_pay:
                print(f'pay {username}')
                ret = und_reward.send_reward(
                    username, is_user=True, num_users=num_users)
                log.debug(ret)

            log.debug(f"Pay provider {providing_app.name}")
            ret = und_reward.send_reward(providing_app.name, False)
            log.debug(ret)

            log.debug(f"Pay Unification")
            ret = und_reward.pay_unif()
            log.debug(ret)

        return self.persist_data(
            providing_app.name, request_hash, d)

    def read_data_from_store(
            self, providing_app: Provider, request_hash):
        temp_dir = Path(tempfile.gettempdir())

        tp = temp_dir / Path(f"{providing_app.name}-{request_hash}")
        encrypted_body = tp.read_text()

        d = json.loads(encrypted_body)

        bundle_d = unbundle(self.keystore, providing_app.name, d)
        decrypted_body = bundle_d['data']

        log.info(f'Decrypted content from persistence store: {decrypted_body}')
        return decrypted_body

    def process_permissions_batch(self, providing_app: Provider):
        r = providing_app.get('process_permission_batch')
        d = r.json()

        if r.status_code != 200:
            raise Exception(d['message'])

        log.debug(d)
