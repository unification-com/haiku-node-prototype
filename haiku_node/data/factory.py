import json
import logging

from haiku_node.blockchain.eos.mother import UnificationMother
from haiku_node.blockchain.eos.uapp import UnificationUapp
from haiku_node.blockchain_helpers.eos import eosio_account
from haiku_node.config.config import UnificationConfig
from haiku_node.data.transform_data2 import TransformDataJSON
from haiku_node.lookup.eos_lookup import UnificationLookup, default_db
from haiku_node.network.eos import get_cleos

log = logging.getLogger(__name__)


class UnificationDataFactory:

    def __init__(self, eos_client, acl_contract_acc, requesting_app, users):
        """

        :param users: A list of users we want to obtain data for. If an empty
        list is provided, then data for all permissible users are provided.
        """
        self.__acl_contract_acc = acl_contract_acc
        self.__requesting_app = requesting_app
        self.__haiku_conf = UnificationConfig()

        self.__my_mother = UnificationMother(
            eos_client, acl_contract_acc, get_cleos())
        self.__my_uapp_sc = UnificationUapp(eos_client, acl_contract_acc)
        self.__my_lookup = UnificationLookup(default_db())
        self.__users = None if len(users) == 0 else users

        self.__my_db_schemas = self.__my_uapp_sc.get_all_db_schemas()
        self.__db_schema_maps = {}
        self.__granted = []
        self.__revoked = []
        self.__raw_data = None

        self.__native_user_meta = self.__my_lookup.get_native_user_meta()

        for pkey, db_schema in self.__my_db_schemas.items():
            schema_map = self.__my_lookup.get_schema_map(pkey)
            self.__db_schema_maps[pkey] = schema_map

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
                    native_user_ids.append(
                        self.__my_lookup.get_native_user_id(u))

        return native_user_ids

    def __generate_data(self):
        self.__granted, self.__revoked = \
            self.__my_uapp_sc.get_perms_for_req_app(self.__requesting_app)

        native_user_ids = self.__generate_user_list()

        # temporary - there's only 1 db schema per app at the moment
        sc_schema_pkey = self.__my_db_schemas[0]['pkey']
        db_schema = self.__my_db_schemas[0]['schema']
        db_schema_map = self.__db_schema_maps[sc_schema_pkey]
        db_connection = self.__haiku_conf['db_conn']["0"]

        cols_to_include = []
        base64_encode_cols = []
        for items in db_schema['fields']:
            if items['table'] != 'unification_lookup':
                real_table_data = self.__my_lookup.get_real_table_info(
                    sc_schema_pkey, items['table'])
                items['table'] = real_table_data['real_table_name']
                cols_to_include.append(items['name'])
                if items['type'] == 'base64_mime_image':
                    base64_encode_cols.append(items['name'])
            else:
                real_table_data = self.__my_lookup.get_real_table_info(
                    sc_schema_pkey, 'data_1')
                items['table'] = real_table_data['real_table_name']
                cols_to_include.append(real_table_data['user_id_column'])

        # temp
        user_table_info =\
            self.__my_lookup.get_real_table_info(sc_schema_pkey, 'users')
        data_table_info = \
            self.__my_lookup.get_real_table_info(sc_schema_pkey, 'data_1')
        
        # generate db params for ETL
        data_source_parms = {
            'database': db_schema_map['db_name'],
            'filename': db_connection['filename'],
            'userTable': user_table_info['real_table_name'],  # temp
            'dataTable': data_table_info['real_table_name'],  # temp
            'userIdentifier': user_table_info['user_id_column'],  # temp
            'dataUserIdentifier': data_table_info['user_id_column'],  # temp
            'dataColumnsToInclude': cols_to_include,
            'native_user_ids': native_user_ids,
            'base64_encode_cols': base64_encode_cols,
            'providing_app': self.__acl_contract_acc,
            'db_schema': db_schema
        }

        # grab list of EOS account names
        if len(native_user_ids) > 0:
            unification_ids = {}
            for n_id in native_user_ids:
                unification_ids[n_id] = self.__my_lookup.get_eos_account(n_id)
            
            data_source_parms['unification_id_map'] = unification_ids
            data_transform_json = TransformDataJSON(data_source_parms)

            j = data_transform_json.transform()
            self.__raw_data = j

        else:
            d = {
                "no-data": True
            }
            self.__raw_data = json.dumps(d)
