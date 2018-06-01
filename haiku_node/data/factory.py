import xml.etree.ElementTree as etree

from haiku_node.blockchain.mother import UnificationMother
from haiku_node.blockchain.acl import UnificationACL
from haiku_node.eosio_helpers import eosio_account
from haiku_node.lookup.eos_lookup import UnificationLookup
from haiku_node.config.keys import get_public_key
from haiku_node.validation.encryption import encrypt
from haiku_node.config.config import UnificationConfig


class UnificationDataFactory:

    def __init__(self, eos_client, acl_contract_acc, requesting_app, users=None):
        self.__acl_contract_acc = acl_contract_acc
        self.__requesting_app = requesting_app
        self.__haiku_conf = UnificationConfig()

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

        # temporary hack - there's only 1 db schema per app at the moment....
        db_schema_name = self.__my_db_schemas[0]['schema_name_str']
        db_schema = self.__my_db_schemas[0]['schema']
        db_schema_map = self.__db_schema_maps[db_schema_name]
        db_connection = self.__haiku_conf['db_conn'][db_schema_name]

        # FOR TESTING
        # db_schema = "<schema-template><fields><field><name>account_name</name><type>varchar</type><is-null>false</is-null><table>unification_lookup</table></field><field><name>Heartrate</name><type>int</type><is-null>true</is-null><table>data_1</table></field><field><name>GeoLocation</name><type>int</type><is-null>true</is-null><table>data_1</table></field><field><name>TimeStamp</name><type>int</type><is-null>true</is-null><table>data_1</table></field><field><name>Pulse</name><type>int</type><is-null>true</is-null><table>data_1</table></field></fields></schema-template>"
        tree = etree.ElementTree(etree.fromstring(db_schema))

        fields = tree.findall('fields/field')

        cols_to_include = []

        for field in fields:
            table = field.find('table')
            col = field.find('name')
            if table.text != 'unification_lookup':
                print("table.text before:", table.text)
                real_table_data = self.__my_lookup.get_real_table_info(db_schema_name, table.text)
                print(real_table_data)
                table.text = real_table_data['real_table_name']
                print("table.text after:", table.text)
                cols_to_include.append(col.text)

        root = tree.getroot()
        db_schema = etree.tostring(root)

        print("new db schema")
        print(db_schema)

        # temp hack
        user_table_info = self.__my_lookup.get_real_table_info(db_schema_name, 'users')
        data_table_info = self.__my_lookup.get_real_table_info(db_schema_name, 'data_1')

        # generate db params for ETL
        data_source_parms = {
            'odbc': 'mysql+mysqldb',  # TODO: get from db schema/conn/config
            'database': db_schema_map['db_name'],
            'host': db_connection['host'],
            'user': db_connection['user'],
            'pass': db_connection['pass'],
            'userTable': user_table_info['real_table_name'],  # temp hack
            'dataTable': data_table_info['real_table_name'],  # temp hack
            'userIdentifier': user_table_info['user_id_column'],  # temp hack
            'dataUserIdentifier': data_table_info['user_id_column'],  # temp hack
            'dataColumnsToInclude': cols_to_include
        }

        print("data_source_parms")
        print(data_source_parms)
        # TODO #1 - plug in Shawn's ETL. Pass native_user_ids, data_source_parms
        # TODO #2 - transform native IDs to EOS acc names

        self.__raw_data = 'DATA'  # plug in Shawn's ETL

        self.__encrypted_data = encrypt(get_public_key(self.__requesting_app), self.__raw_data)
