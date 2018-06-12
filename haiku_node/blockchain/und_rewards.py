import os
import json
import logging
import subprocess

from eosapi import Client
from haiku_node.config.config import UnificationConfig
from haiku_node.blockchain.acl import UnificationACL

log = logging.getLogger(__name__)


class UndRewards:
    def __init__(self):
        conf = UnificationConfig()
        self.__my_acl_acc = os.environ['app_name']
        self.__eos_client_pre = ["/opt/eosio/bin/cleos", "--url", f"http://{conf['eos_rpc_ip']}:{conf['eos_rpc_port']}",
                                 "--wallet-url", f"http://{conf['eos_wallet_ip']}:{conf['eos_wallet_port']}"]

        eos_client = Client(
            nodes=[f"http://{conf['eos_rpc_ip']}:{conf['eos_rpc_port']}"])

        acl = UnificationACL(eos_client, self.__my_acl_acc)

        self.__user_und_reward = acl.get_user_und_reward()
        self.__app_und_reward = acl.get_app_und_reward()

    def send_reward(self, to, is_user=True):

        if is_user:
            reward = self.__user_und_reward
        else:
            reward = self.__app_und_reward

        d = {
            'from': self.__my_acl_acc,
            'to': to,
            'quantity': f'{reward}.0000 UND',  # TODO - need to fix precision
            'memo': 'UND Reward'
        }
        # cleos push action eosio.token transfer '[ "app3", "user1", "1.0000 UND", "m" ]' -p app3
        subcommands = ["push", "action", "unif.token", "transfer", json.dumps(d), "-p", self.__my_acl_acc]

        cmd = self.__eos_client_pre + subcommands

        log.debug(f"cleos command: {cmd}")

        result = subprocess.run(
            cmd, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, universal_newlines=True)

        log.debug(result.stdout)
        if result.returncode != 0:
            log.warning(result.stdout)
            log.debug(result.stdout)
            log.debug(result.stderr)
            log.debug(' '.join(cmd))

        return result
