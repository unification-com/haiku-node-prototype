import json

from haiku_node.blockchain_helpers.eos import eosio_account
from haiku_node.blockchain_helpers.eos.eos_keys import UnifEosKey
from haiku_node.utils.utils import sha256


class UnificationMother:
    """
    Loads data from MOTHER Smart Contract for a Haiku node's app.
    """

    def __init__(self, eos_client,
                 uapp_contract_acc, cleos_client, ipfs_client):
        """
        :param uapp_contract_acc: the eos account name of the app for which the
            class will retrieve data from the ACL/Meta Data smart contract.
        """
        self.__mother = "unif.mother"
        self.__valid_apps_table = "validapps"
        self.__uapp_contract_acc = uapp_contract_acc
        self.__eosClient = eos_client
        self.__is_valid_app = False
        self.__is_valid_code = False
        self.__signed_by_mother = False
        self.__deployed_contract_hash = ""  # the actual deployed contract
        self.__uapp_sc_hash_in_mother = ""  # hash held in MOTHER
        self.__haiku_rpc_server_ip = None
        self.__haiku_rpc_server_port = None
        self.__cleos = cleos_client
        self.__ipfs_client = ipfs_client

        self.__run()

    def valid_app(self):
        return self.__is_valid_app

    def valid_code(self):
        return self.__is_valid_code

    def get_hash_in_mother(self):
        return self.__uapp_sc_hash_in_mother

    def signed_by_mother(self):
        return self.__signed_by_mother

    def get_deployed_contract_hash(self):
        return self.__deployed_contract_hash

    def get_haiku_rpc_server(self):
        return f'https://{self.__haiku_rpc_server_ip}:' \
               f'{self.__haiku_rpc_server_port}'

    def get_haiku_rpc_ip(self):
        return self.__haiku_rpc_server_ip

    def get_haiku_rpc_port(self):
        return self.__haiku_rpc_server_port

    def __get_contract_hash(self):
        prefix = 'code hash: '
        result = self.__cleos.run(['get', 'code', self.__uapp_contract_acc])
        return result.stdout.strip()[len(prefix):]

    def __call_mother(self):
        """
        Call the Mother Smart Contract, and check if the requesting_app is both
        a verified app, and that it's smart contract code is valid (by checking
        the code's hash).
        """
        self.__deployed_contract_hash = self.__get_contract_hash()

        table_data = self.__eosClient.get_table_rows(
            self.__mother, self.__mother, self.__valid_apps_table, True, 0, -1,
            -1)

        req_app_uint64 = eosio_account.string_to_name(self.__uapp_contract_acc)

        for i in table_data['rows']:

            if int(i['acl_contract_acc']) == req_app_uint64:
                ipfs_hash = i['ipfs_hash']
                uapp_json_str = self.__ipfs_client.get_json(ipfs_hash)
                uapp_json = json.loads(uapp_json_str)
                uapp_data = uapp_json['data']
                mother_sig = uapp_json['sig']

                mother_public_key = self.__cleos.get_public_key(
                    self.__mother, 'active')

                eosk = UnifEosKey()
                digest_sha = sha256(json.dumps(uapp_data).encode('utf-8'))
                self.__signed_by_mother = eosk.verify_pub_key(
                    mother_sig, digest_sha, mother_public_key)

                if int(i['is_valid']) == 1:
                    self.__is_valid_app = True
                if (uapp_data['acl_contract_hash']
                        == self.__deployed_contract_hash):
                    self.__is_valid_code = True
                self.__uapp_sc_hash_in_mother = uapp_data['acl_contract_hash']
                self.__haiku_rpc_server_ip = uapp_data['rpc_server_ip']
                self.__haiku_rpc_server_port = uapp_data['rpc_server_port']
                break

    def __run(self):
        self.__call_mother()
