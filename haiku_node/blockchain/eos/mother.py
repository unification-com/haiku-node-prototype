from haiku_node.blockchain_helpers.eos import eosio_account
from haiku_node.network.eos import get_cleos


class UnificationMother:
    """
    Loads data from MOTHER Smart Contract for a Haiku node's app.
    """

    def __init__(self, eos_client, acl_contract_acc):
        """
        :param acl_contract_acc: the eos account name of the app for which the
            class will retrieve data from the ACL/Meta Data smart contract.
        """
        self.__mother = "unif.mother"
        self.__valid_apps_table = "validapps"
        self.__acl_contract_acc = acl_contract_acc
        self.__eosClient = eos_client
        self.__is_valid_app = False
        self.__is_valid_code = False
        self.__deployed_contract_hash = ""  # the actual deployed contract
        self.__acl_contract_hash_in_mother = ""  # hash held in MOTHER
        self.__haiku_rpc_server_ip = None
        self.__haiku_rpc_server_port = None

        #TODO: Don't instantiate in the __init__, but find all the usages and
        # pass it in instead
        self.__cleos = get_cleos()

        self.__run()

    def valid_app(self):
        return self.__is_valid_app

    def valid_code(self):
        return self.__is_valid_code

    def get_hash_in_mother(self):
        return self.__acl_contract_hash_in_mother

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
        result = self.__cleos.run(['get', 'code', self.__acl_contract_acc])
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

        req_app_uint64 = eosio_account.string_to_name(self.__acl_contract_acc)

        for i in table_data['rows']:

            if int(i['acl_contract_acc']) == req_app_uint64:
                if int(i['is_valid']) == 1:
                    self.__is_valid_app = True
                if i['acl_contract_hash'] == self.__deployed_contract_hash:
                    self.__is_valid_code = True
                self.__acl_contract_hash_in_mother = i['acl_contract_hash']
                self.__haiku_rpc_server_ip = i['rpc_server_ip']
                self.__haiku_rpc_server_port = i['rpc_server_port']
                break

    def __run(self):
        self.__call_mother()
