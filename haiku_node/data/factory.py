import xml.etree.ElementTree as etree

import json
from xmljson import parker, Parker
from lxml.etree import fromstring, tostring

from haiku_node.blockchain.mother import UnificationMother
from haiku_node.blockchain.acl import UnificationACL
from haiku_node.config.config import UnificationConfig
from haiku_node.data.transform_data import TransformData
from haiku_node.blockchain_helpers import eosio_account
from haiku_node.lookup.eos_lookup import UnificationLookup, default_db


class UnificationDataFactory:

    def __init__(self, eos_client, acl_contract_acc, requesting_app, users):
        """

        :param users: A list of users we want to obtain data for. If an empty
        list is provided, then data for all permissible users are provided.
        """
        self.__acl_contract_acc = acl_contract_acc
        self.__requesting_app = requesting_app
        self.__haiku_conf = UnificationConfig()

        self.__my_mother = UnificationMother(eos_client, acl_contract_acc)
        self.__my_acl = UnificationACL(eos_client, acl_contract_acc)
        self.__my_lookup = UnificationLookup(default_db())
        self.__users = None if len(users) == 0 else users

        self.__valid_db_schemas = self.__my_mother.get_valid_db_schemas()
        self.__my_db_schemas = []
        self.__db_schema_maps = {}
        self.__granted = []
        self.__revoked = []
        self.__raw_data = None

        self.__native_user_meta = self.__my_lookup.get_native_user_meta()

        for schema, vers in self.__valid_db_schemas.items():
            self.__my_db_schemas.append(self.__my_acl.get_current_valid_schema(schema, vers))
            schema_map = self.__my_lookup.get_schema_map(schema)
            self.__db_schema_maps[schema] = schema_map

        self.__generate_data()

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

        print("native_user_ids")
        print(native_user_ids)
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
        ###(Refer to the comment in Asana)
        ### 1. have the schema in JSON from the beginning
        ### 2. convert XML to JSON here
        ### Currently we are going with 2.

        print(db_schema)

        cols_to_include = []
        base64_encode_cols = []
        for items in db_schema['fields']:
            if items['table'] != 'unification_lookup':
                print('table.text before:', items['table'])
                real_table_data = self.__my_lookup.get_real_table_info(db_schema_name, items['table'])
                print(real_table_data)
                items['table'] = real_table_data['real_table_name']
                print('table text after:', items['table'])
                cols_to_include.append(items['name'])
                if items['type'] == 'base64_mime_image':
                    base64_encode_cols.append(items['name'])
            else:
                real_table_data = self.__my_lookup.get_real_table_info(db_schema_name, 'data_1')
                items['table'] = real_table_data['real_table_name']
                cols_to_include.append(real_table_data['user_id_column'])

        print(base64_encode_cols)

        # print("new db schema")
        # print(db_schema)

        # temp hack
        user_table_info = self.__my_lookup.get_real_table_info(db_schema_name, 'users')
        data_table_info = self.__my_lookup.get_real_table_info(db_schema_name, 'data_1')
        
        # generate db params for ETL
        data_source_parms = {
            'odbc': 'mysql+mysqlconnector',  # TODO: set/get from db schema/conn/config
            'database': db_schema_map['db_name'],
            'host': db_connection['host'],
            'port': db_connection['port'],
            'user': db_connection['user'],
            'pass': db_connection['pass'],
            'userTable': user_table_info['real_table_name'],  # temp hack
            'dataTable': data_table_info['real_table_name'],  # temp hack
            'userIdentifier': user_table_info['user_id_column'],  # temp hack
            'dataUserIdentifier': data_table_info['user_id_column'],  # temp hack
            'dataColumnsToInclude': cols_to_include,
            'native_user_ids': native_user_ids,
            'base64_encode_cols': base64_encode_cols,
            'providing_app': self.__acl_contract_acc
        }

        # TEMP FOR TESTING
        print("data_source_parms")
        print(data_source_parms)
        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(data_source_parms)
        # print("native User IDs for Query")
        # print(native_user_ids)

        # grab list of EOS account names
        if len(native_user_ids) > 0:
            unification_ids = {}
            for id in native_user_ids:
                unification_ids[id] = self.__my_lookup.get_eos_account(id)
            
            data_source_parms['unification_ids'] = unification_ids
            data_transform = TransformData(data_source_parms)
            #### transforms xml data to json dictionary (string)

            xml = fromstring(data_transform.fetch_user_data())
            self.__raw_data = json.dumps(parker.data(xml, preserve_root=True))

            #self.__raw_data = data_transform.fetch_user_data()
        else:
            d = {
                "no-data": True
            }
            self.__raw_data = json.dumps(d)  # temp dummy message for no users granting perms
