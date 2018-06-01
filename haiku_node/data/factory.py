from haiku_node.blockchain.mother import UnificationMother
from haiku_node.blockchain.acl import UnificationACL
from haiku_node.eosio_helpers import eosio_account
from haiku_node.lookup.eos_lookup import UnificationLookup
from haiku_node.config.keys import get_public_key
from haiku_node.validation.encryption import encrypt


class UnificationDataFactory:

    def __init__(self, eos_client, acl_contract_acc, requesting_app, users=None):
        self.__acl_contract_acc = acl_contract_acc
        self.__requesting_app = requesting_app

        self.__my_mother = UnificationMother(eos_client, acl_contract_acc)
        self.__my_acl = UnificationACL(eos_client, acl_contract_acc)
        self.__my_lookup = UnificationLookup()
        self.__users = users

        self.__valid_db_schemas = self.__my_mother.get_valid_db_schemas()
        self.__my_db_schemas = []
        self.__db_schema_maps = {}
        self.__granted = []
        self.__revoked = []
        self.__raw_data = None
        self.__encrypted_data = None

        self.__native_user_meta = self.__my_lookup.get_native_user_meta()

        for schema, vers in self.__valid_db_schemas.items():
            self.__my_db_schemas.append(self.__my_acl.get_current_valid_schema(schema, vers))
            schema_map = self.__my_lookup.get_schema_map(schema)
            self.__db_schema_maps[schema] = schema_map

        self.__generate_data()

    def get_encrypted_data(self):
        return self.__encrypted_data

    def get_raw_data(self):
        return self.__raw_data

    def __generate_user_list(self):
        native_user_ids = []

        if self.__users is None:
            for i in self.__granted:
                native_user_ids.append(
                    self.__my_lookup.get_native_user_id(
                        eosio_account.name_to_string(i)
                    ))
        else:
            for u in self.__users:
                user_acc_uint64 = eosio_account.string_to_name(u)
                if user_acc_uint64 in self.__granted:
                    native_user_ids.append(self.__my_lookup.get_native_user_id(u))

        return native_user_ids

    def __generate_data(self):
        self.__granted, self.__revoked = self.__my_acl.get_perms_for_req_app(self.__requesting_app)

        native_user_ids = self.__generate_user_list()

        # TODO #1 - plug in Shawn's ETL. Pass native_user_ids, self.__db_schema_maps, self.__native_user_meta
        # TODO #2 - either transform native IDs to EOS acc names here,
        # or do in the XML generation in ETL

        self.__raw_data = 'DATA'  # plug in Shawn's ETL

        self.__encrypted_data = encrypt(get_public_key(self.__requesting_app), self.__raw_data)
