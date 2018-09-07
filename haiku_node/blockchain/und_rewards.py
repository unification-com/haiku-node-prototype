import json
import logging
import subprocess

from eosapi import Client

from haiku_node.config.config import UnificationConfig
from haiku_node.blockchain.uapp import UnificationUapp

log = logging.getLogger(__name__)
UNIF = 0.03
DATA_PROVIDER = 0.3
END_USERS = 0.67


class UndRewards:
    def __init__(self, acl_acc: str):
        """

        :param acl_acc: The account name of the payer.
        """
        self.__my_acl_acc = acl_acc
        conf = UnificationConfig()
        self.__eos_client_pre = ["/opt/eosio/bin/cleos", "--url", f"http://{conf['eos_rpc_ip']}:{conf['eos_rpc_port']}",
                                 "--wallet-url", f"http://{conf['eos_wallet_ip']}:{conf['eos_wallet_port']}"]

        eos_client = Client(
            nodes=[f"http://{conf['eos_rpc_ip']}:{conf['eos_rpc_port']}"])

        uapp_sc = UnificationUapp(eos_client, self.__my_acl_acc)

        schemas = uapp_sc.get_all_db_schemas()
        # Todo: get correct price for schema being used. Temporary solution since only 1 schema per app in prototype
        self.__und_scheduled = schemas[0]['price_sched']
        self.__und_adhoc = schemas[0]['price_adhoc']

    def send_reward(self, to, is_user=True, num_users=1):

        # Todo: migrate to Token smart contract
        if is_user:
            reward = "{0:.4f}".format(round(float((self.__und_scheduled * END_USERS) / num_users), 4))
        else:
            reward = "{0:.4f}".format(round(float(self.__und_scheduled * DATA_PROVIDER), 4))

        d = {
            'from': self.__my_acl_acc,
            'to': to,
            'quantity': f'{reward} UND',
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

    def pay_unif(self):
        und = "{0:.4f}".format(round(float(self.__und_scheduled * UNIF), 4))

        d = {
            'from': self.__my_acl_acc,
            'to': 'unif.mother',
            'quantity': f'{und} UND',
            'memo': 'UND Reward'
        }

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

    def calculate_reward(self, is_user=True, num_users=1):
        if is_user:
            reward = round(float((self.__und_scheduled * END_USERS) / num_users), 4)
        else:
            reward = round(float(self.__und_scheduled * DATA_PROVIDER), 4)

        return reward
