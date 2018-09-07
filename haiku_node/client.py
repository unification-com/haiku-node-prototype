import json
import tempfile
from pathlib import Path
from eosapi import Client

import logging
import requests

from haiku_node.blockchain.und_rewards import UndRewards
from haiku_node.config.config import UnificationConfig
from haiku_node.encryption.payload import bundle, unbundle
from haiku_node.validation.validation import UnificationAppScValidation


log = logging.getLogger(__name__)


class Provider:
    def __init__(self, name, protocol, host, port):
        self.name = name
        self.protocol = protocol
        self.host = host
        self.port = port

    def base_url(self):
        return f"{self.protocol}://{self.host}:{self.port}"


class HaikuDataClient:
    def __init__(self, keystore, protocol='https', local=False):
        self.keystore = keystore
        self.local = local
        self.protocol = protocol

    def transform_request_id(self, user, request_hash, client_type, request_id=None):
        """
        # TODO: Convert to a particular request body
        """
        return {
            'users': [] if user is None else [user],
            'data_id': request_hash,
            'request_id': request_id,
            'client_type': client_type
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

        # Check if the providing app is valid according to MOTHER
        conf = UnificationConfig()
        eos_client = Client(
            nodes=[f"http://{conf['eos_rpc_ip']}:{conf['eos_rpc_port']}"])

        v = UnificationAppScValidation(
            eos_client, conf['acl_contract'],  providing_app.name,
            get_perms=True)

        if not v.valid():
            raise Exception(f"Providing App {providing_app.name} is "
                            f"NOT valid according to MOTHER")

        body = self.transform_request_id(user, request_hash, 'enterprise')
        payload = bundle(
            self.keystore, requesting_app, providing_app.name, body, 'Success')

        base = providing_app.base_url()
        r = requests.post(f"{base}/data_request", json=payload, verify=False)
        d = r.json()

        if r.status_code != 200:
            raise Exception(d['message'])

        bundle_d = unbundle(self.keystore, providing_app.name, d)
        decrypted_body = bundle_d['data']

        log.info(f'"In the air" decrypted content is: {decrypted_body}')

        # TODO: only pay if data is valid
        und_reward = UndRewards(requesting_app)

        json_obj = json.loads(decrypted_body)

        if 'no-data' not in json_obj:
            users_to_pay = json_obj['data']['unification_users']['unification_user']
            print("users_to_pay")
            print(users_to_pay)
            if isinstance(users_to_pay, list):
                num_users = len(users_to_pay)
                print(f"Pay {num_users} users")
                for username in users_to_pay:
                    print(f'pay {username}')
                    ret = und_reward.send_reward(username, is_user=True, num_users=num_users)
                    log.debug(ret)
            else:
                print(f'pay single user {users_to_pay}')
                ret = und_reward.send_reward(users_to_pay, is_user=True, num_users=1)
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

    def make_data_request_uapp_store(self, requesting_app, providing_app: Provider, request_id, request_hash):
        # Check if the providing app is valid according to MOTHER
        conf = UnificationConfig()
        eos_client = Client(
            nodes=[f"http://{conf['eos_rpc_ip']}:{conf['eos_rpc_port']}"])

        v = UnificationAppScValidation(
            eos_client, conf['acl_contract'], providing_app.name,
            get_perms=True)

        if not v.valid():
            raise Exception(f"Providing App {providing_app.name} is "
                            f"NOT valid according to MOTHER")

        body = self.transform_request_id(None, request_hash, 'standard', request_id)
        payload = bundle(
            self.keystore, requesting_app, providing_app.name, body, 'Success')

        base = providing_app.base_url()
        r = requests.post(f"{base}/data_request", json=payload, verify=False)
        d = r.json()

        if r.status_code != 200:
            raise Exception(d['message'])

        bundle_d = unbundle(self.keystore, providing_app.name, d)
        decrypted_body = bundle_d['data']

        print(f'"In the air" decrypted content is: {decrypted_body}')

        return self.persist_data(
            providing_app.name, request_hash, d)
