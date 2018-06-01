class UnificationACL:
    """
    Loads data from ACL/Meta Smart Contract for a Haiku node's app
    """

    def __init__(self, eos_client, acl_contract_acc):
        """
        :param acl_contract_acc: the eos account name of the app for which the
            class will retrieve data from the ACL/Meta Data smart contract
        """
        self.__permission_rec_table = "permrecords"
        self.__db_schema_table = "dataschemas"
        self.__data_sources_table = "datasources"

        self.__acl_contract_acc = acl_contract_acc
        self.__eosClient = eos_client

        self.__db_schemas = {}
        self.__data_sources = {}

        self.__run()

    def get_db_schemas(self):
        return self.__db_schemas

    def get_data_sources(self):
        return self.__data_sources

    def get_current_valid_schema(self, schema_name, schema_vers):
        if f'{schema_name}.{schema_vers}' in self.__db_schemas:
            return self.__db_schemas[f'{schema_name}.{schema_vers}']
        else:
            return False

    def get_perms_for_req_app(self, requesting_app):
        # TODO: run in loop and check JSON result for "more" value
        table_data = self.__eosClient.get_table_rows(
            requesting_app,
            self.__acl_contract_acc, self.__permission_rec_table, True, 0, -1,
            -1)

        granted = []
        revoked = []

        for i in table_data['rows']:
            if int(i['permission_granted']) == 1:
                granted.append(int(i['user_account']))
            else:
                revoked.append(int(i['user_account']))

        return granted, revoked

    def __load_db_schemas(self):
        table_data = self.__eosClient.get_table_rows(
            self.__acl_contract_acc,
            self.__acl_contract_acc, self.__db_schema_table, True, 0, -1, -1)

        for i in table_data['rows']:
            key = f'{i["schema_name_str"]}.{i["schema_vers"]}'
            d = {
                'schema_id': i['pkey'],
                'schema_name': i['schema_name'],
                'schema_name_str': i['schema_name_str'],
                'schema_vers': i['schema_vers'],
                'schema': i['schema']
            }
            self.__db_schemas[key] = d

    def __load_data_sources(self):
        table_data = self.__eosClient.get_table_rows(
            self.__acl_contract_acc,
            self.__acl_contract_acc, self.__data_sources_table, True, 0, -1, -1)

        for i in table_data['rows']:
            source_name = i['source_name']
            d = {
                'pkey': i['pkey'],
                'source_name': i['source_name'],
                'source_name_str': i['source_name_str'],
                'source_type': i['source_type'],
                'schema_id': i['schema_id'],
                'acl_contract_acc': i['acl_contract_acc'],
                'in_use': i['in_use']
            }
            self.__data_sources[source_name] = d

    def __run(self):
        self.__load_db_schemas()
        self.__load_data_sources()