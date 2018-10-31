import json
import logging
import subprocess
import time
import string
import random

from haiku_node.config.config import UnificationConfig
from haiku_node.network.eos import get_cleos

log = logging.getLogger(__name__)

UNIF = 0.03
DATA_PROVIDER = 0.3
END_USERS = 0.67


class UndRewards:
    def __init__(self, acl_acc: str, und_amt: int):
        """

        :param acl_acc: The account name of the payer.
        :param und_amt: The amount of UND to be processed
        """
        self.__my_acl_acc = acl_acc
        self.__cleos = get_cleos()

        #TODO: I think I can deprecate the following
        conf = UnificationConfig()
        self.__eos_client_pre = [
            "/opt/eosio/bin/cleos", "--url",
            f"http://{conf['eos_rpc_ip']}:{conf['eos_rpc_port']}",
            "--wallet-url",
            f"http://{conf['eos_wallet_ip']}:{conf['eos_wallet_port']}"]

        self.__und_amt = und_amt

    def send_reward(self, to, is_user=True, num_users=1):

        reward = "{0:.4f}".format(self.calculate_reward(is_user, num_users))

        reward_timestamp = "%.20f" % time.time()

        d = {
            'from': self.__my_acl_acc,
            'to': to,
            'quantity': f'{reward} UND',
            'memo': f'UND Reward {self.tx_id_generator()} {reward_timestamp}'
        }

        log.debug(f"{self.__my_acl_acc} is paying {to} {reward} UND")

        subcommands = [
            "push", "action", "unif.token", "transfer",
            json.dumps(d), "-p", self.__my_acl_acc]

        result = self.__cleos.run(subcommands)

        return result

    def pay_unif(self):
        und = "{0:.4f}".format(round(float(self.__und_amt * UNIF), 4))

        reward_timestamp = "%.20f" % time.time()

        d = {
            'from': self.__my_acl_acc,
            'to': 'unif.mother',
            'quantity': f'{und} UND',
            'memo': f'UND Tax {self.tx_id_generator()} {reward_timestamp}'
        }

        subcommands = [
            "push", "action", "unif.token", "transfer", json.dumps(d),
            "-p", self.__my_acl_acc]

        result = self.__cleos.run(subcommands)

        return result

    def calculate_reward(self, is_user=True, num_users=1):

        # Todo: migrate to Token smart contract
        if is_user:
            reward = round(
                float((self.__und_amt * END_USERS) / num_users), 4)
        else:
            reward = round(float(self.__und_amt * DATA_PROVIDER), 4)

        return reward

    @staticmethod
    def tx_id_generator(size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))
