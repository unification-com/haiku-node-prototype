from haiku_node.blockchain_helpers import eosio_account


class UnificationMother:
    """
    Loads data from MOTHER Smart Contract for a Haiku node's app
    """

    def __init__(self, eos_client, acl_contract_acc):
        """
        :param acl_contract_acc: the eos account name of the app for which the
            class will retrieve data from the ACL/Meta Data smart contract
        """
        self.__mother = "unif.mother"
        self.__valid_apps_table = "validapps"
        self.__acl_contract_acc = acl_contract_acc
        self.__eosClient = eos_client
        self.__is_valid_app = False
        self.__is_valid_code = False
        self.__deployed_contract_hash = ""  # the actual deployed contract
        self.__valid_db_schemas = {}
        self.__acl_contract_hash_in_mother = ""  # hash held in MOTHER
        self.__haiku_rpc_server_ip = None
        self.__haiku_rpc_server_port = None

        self.__run()

    def valid_app(self):
        return self.__is_valid_app

    def valid_code(self):
        return self.__is_valid_code

    def get_hash_in_mother(self):
        return self.__acl_contract_hash_in_mother

    def get_deployed_contract_hash(self):
        return self.__deployed_contract_hash

    def get_valid_db_schemas(self):
        return self.__valid_db_schemas

    def get_haiku_rpc_server(self):
        return f'https://{self.__haiku_rpc_server_ip}:' \
               f'{self.__haiku_rpc_server_port}'

    def get_haiku_rpc_ip(self):
        return self.__haiku_rpc_server_ip

    def get_haiku_rpc_port(self):
        return self.__haiku_rpc_server_port

    def __call_mother(self):
        """
        Call the Mother Smart Contract, and check if the requesting_app is both
        a verified app, and that it's smart contract code is valid (by checking
        the code's hash).
        """
        json_data = self.__eosClient.get_code(self.__acl_contract_acc)
        self.__deployed_contract_hash = json_data['code_hash']

        table_data = self.__eosClient.get_table_rows(
            self.__mother, self.__mother, self.__valid_apps_table, True, 0, -1,
            -1)

        req_app_uint64 = eosio_account.string_to_name(self.__acl_contract_acc)

        db_schemas = ""

        for i in table_data['rows']:

            if int(i['acl_contract_acc']) == req_app_uint64:
                if int(i['is_valid']) == 1:
                    self.__is_valid_app = True
                if i['acl_contract_hash'] == self.__deployed_contract_hash:
                    self.__is_valid_code = True
                self.__acl_contract_hash_in_mother = i['acl_contract_hash']
                self.__haiku_rpc_server_ip = i['rpc_server_ip']
                self.__haiku_rpc_server_port = i['rpc_server_port']
                db_schemas = i['schema_vers']
                break

        if len(db_schemas) > 0:
            schemas_vers = db_schemas.split(",")
            for sv in schemas_vers:
                schema, vers = sv.split(":")
                self.__valid_db_schemas[schema] = vers

    def __run(self):
        self.__call_mother()
