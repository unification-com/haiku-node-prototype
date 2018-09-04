import logging
import subprocess
import requests


KEOS_IP = 'keosd'
KEOS_PORT = 8889

NODEOS_IP = 'nodeosd'
NODEOS_PORT = 8888

BLOCK_SLEEP = 0.5

log = logging.getLogger(__name__)


class EosioCleos:
    def __init__(self, host=False):
        """

        :param host: Set to True if not operating from a Docker container (
        i.e. from the host machine)
        """
        self.host = host
        if host:
            self.nodeos = f"http://127.0.0.1:{NODEOS_PORT}"
            self.keosd = f"http://127.0.0.1:{KEOS_PORT}"
            self.nodeos_ip = '127.0.0.1'

        else:
            self.nodeos = f"http://{NODEOS_IP}:{NODEOS_PORT}"
            self.keosd = f"http://{KEOS_IP}:{KEOS_PORT}"
            self.nodeos_ip = NODEOS_IP

    def keos_url(self):
        return self.keosd

    def request_keos(self, endpoint):
        return f"{self.keosd}/{endpoint}"

    def get_nodeos_url(self):
        return self.nodeos

    def run(self, subcommands):
        if self.host:
            pre = ["/usr/local/bin/docker", "exec", "keosd",
                   "/opt/eosio/bin/cleos", "--url", self.nodeos,
                   "--wallet-url", self.keosd]
        else:
            pre = ["/opt/eosio/bin/cleos", "--url", self.nodeos,
                   "--wallet-url", self.keosd]

        cmd = pre + subcommands

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

    def open_wallet(self, username):
        """
        Wallets need to be opened.
        """
        log.info('Opening wallet')
        r = requests.post(self.request_keos('v1/wallet/list_wallets'))
        current_users = [x.strip(' *') for x in r.json()]
        if username not in current_users:
            url = f"{self.keos_url()}/v1/wallet/open"
            r = requests.post(url, data=f""" "{username}" """)
            assert r.status_code == 200

    def lock_wallet(self, username):
        return self.run(["wallet", "lock", "--name", username])

    def unlock_wallet(self, username, password):
        return self.run(
            ["wallet", "unlock", "--name", username, "--password", password])

