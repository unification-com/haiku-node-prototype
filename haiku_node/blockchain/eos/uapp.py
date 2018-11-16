import json
import time

from haiku_node.config.config import UnificationConfig
from haiku_node.network.eos import get_cleos, get_eos_rpc_client


def get_self_uapp():
    conf = UnificationConfig()
    eos_client = get_eos_rpc_client()
    return UnificationUapp(eos_client, conf['acl_contract'])


def unix_timestamp():
    return int(time.time() * 1000)


class UnificationUapp:
    """
     - Loads data from UApp Smart Contract for a Haiku node's app
     - Calls actions in UApp Smart Contract to add/modify data
    """

    def __init__(self, eos_rpc_client, uapp_contract_acc):
        """
        :param eos_rpc_client: EOS RPC Client
        :param uapp_contract_acc: the eos account name of the app for which the
               class will retrieve data from the UApp smart contract

        """
        self.__ipfs_perm_table = "userperms"
        self.__rsa_pub_key_table = "rsapubkey"
        self.__db_schema_table = "dataschemas"
        self.__data_requests_table = "datareqs"

        self.__uapp_contract_acc = uapp_contract_acc
        self.__eos_rpc_client = eos_rpc_client

        # Todo: Migrate from cleos command line to EOS RPC API
        self.__cleos = get_cleos()

    def get_all_db_schemas(self):
        db_schemas = {}

        # Todo: pagination
        table_data = self.__eos_rpc_client.get_table_rows(
            self.__uapp_contract_acc,
            self.__uapp_contract_acc, self.__db_schema_table, True, 0, -1, -1)

        for i in table_data['rows']:
            key = i['pkey']
            d = {
                'pkey': i['pkey'],
                'schema_vers': i['schema_vers'],
                'schema': json.loads(i['schema']),
                'schedule': i['schedule'],
                'price_sched': i['price_sched'],
                'price_adhoc': i['price_adhoc']
            }
            db_schemas[key] = d

        return db_schemas

    def get_db_schema_by_pkey(self, pkey: int):
        """

        :param pkey: Primary Key for the schema table in the smart contract
        :return: db_schema object containing data from the Smart Contract table
        """
        db_schema = {}
        table_data = self.__eos_rpc_client.get_table_rows(
            self.__uapp_contract_acc,
            self.__uapp_contract_acc, self.__db_schema_table, True,
            pkey, pkey + 1, 1)

        if table_data['rows']:
            td = table_data['rows'][0]
            if td['pkey'] == pkey:
                db_schema = {
                    'pkey': td['pkey'],
                    'schema_vers': td['schema_vers'],
                    'schema': json.loads(td['schema']),
                    'schedule': td['schedule'],
                    'price_sched': td['price_sched'],
                    'price_adhoc': td['price_adhoc']
                }

        return db_schema

    def get_ipfs_perms_for_req_app(self, requesting_app):
        table_data = self.__eos_rpc_client.get_table_rows(
            requesting_app,
            self.__uapp_contract_acc, self.__ipfs_perm_table, True, 0, -1,
            -1)

        ipfs_hash = None
        merkle_root = None

        if table_data['rows']:
            ipfs_hash = table_data['rows'][0]['ipfs_hash']
            merkle_root = table_data['rows'][0]['merkle_root']

        return ipfs_hash, merkle_root

    def get_public_key_hash(self, requesting_app):
        table_data = self.__eos_rpc_client.get_table_rows(
            requesting_app,
            self.__uapp_contract_acc, self.__rsa_pub_key_table, True, 0, -1,
            -1)

        rows = table_data['rows']
        return rows[0]['rsa_pub_key']

    def get_all_data_requests(self):
        data_requests = {}
        table_data = self.__eos_rpc_client.get_table_rows(
            self.__uapp_contract_acc,
            self.__uapp_contract_acc,
            self.__data_requests_table, True, 0, -1, -1)

        for i in table_data['rows']:
            key = i['pkey']
            d = {
                'pkey': i['pkey'],
                'provider_name': i['provider_name'],
                'schema_id': i['schema_id'],
                'ts_created': i['ts_created'],
                'ts_updated': i['ts_updated'],
                'req_type': i['req_type'],
                'query': i['query'],
                'price': i['price'],
                'hash': i['hash'],
                'aggr': i['aggr']
            }
            data_requests[key] = d

        return data_requests

    def get_data_request_by_pkey(self, pkey: int):
        data_request = {}
        table_data = self.__eos_rpc_client.get_table_rows(
            self.__uapp_contract_acc,
            self.__uapp_contract_acc, self.__data_requests_table, True,
            pkey, pkey + 1, 1)

        td = table_data['rows'][0]
        if td['pkey'] == pkey:
            data_request = {
                'pkey': td['pkey'],
                'provider_name': td['provider_name'],
                'schema_id': td['schema_id'],
                'req_type': td['req_type'],
                'query': td['query'],
                'price': td['price'],
                'hash': td['hash'],
                'aggr': td['aggr']
            }

        return data_request

    def add_schema(self, schema, schema_vers: int, schedule: int,
                   price_sched: int, price_adhoc: int):

        d = {
            'schema': json.dumps(schema),
            'schema_vers': schema_vers,
            'schedule': schedule,
            'price_sched': price_sched,
            'price_adhoc': price_adhoc
        }
        ret = self.__cleos.run(
            ['push', 'action', self.__uapp_contract_acc,
             'addschema', json.dumps(d), '-p',
             f'{self.__uapp_contract_acc}@modschema'])

        print(ret.stdout)

        return ret

    def edit_schema(self, pkey: int, schema: str, schema_vers: int,
                    schedule: int, price_sched: int, price_adhoc: int):

        d = {
            'pkey': pkey,
            'schema': json.dumps(schema),
            'schema_vers': schema_vers,
            'schedule': schedule,
            'price_sched': price_sched,
            'price_adhoc': price_adhoc
        }
        ret = self.__cleos.run(
            ['push', 'action', self.__uapp_contract_acc, 'editschema',
             json.dumps(d), '-p', f'{self.__uapp_contract_acc}@modschema'])

        print(ret.stdout)

        return ret

    def set_schema_version(self, pkey: int, schema_vers: int):

        d = {
            'pkey': pkey,
            'schema_vers': schema_vers
        }
        ret = self.__cleos.run(
            ['push', 'action', self.__uapp_contract_acc, 'setvers',
             json.dumps(d), '-p', f'{self.__uapp_contract_acc}@modschema'])

        print(ret.stdout)

        return ret

    def set_schema_schedule(self, pkey: int, schedule: int):

        d = {
            'pkey': pkey,
            'schedule': schedule
        }
        ret = self.__cleos.run(
            ['push', 'action', self.__uapp_contract_acc, 'setschedule',
             json.dumps(d), '-p', f'{self.__uapp_contract_acc}@modschema'])

        print(ret.stdout)

        return ret

    def set_schema_price_schedule(self, pkey: int, price_sched: int):

        d = {
            'pkey': pkey,
            'price_sched': price_sched
        }
        ret = self.__cleos.run(
            ['push', 'action', self.__uapp_contract_acc, 'setpricesch',
             json.dumps(d), '-p', f'{self.__uapp_contract_acc}@modschema'])

        print(ret.stdout)

        return ret

    def set_schema_price_adhoc(self, pkey: int, price_adhoc: int):

        d = {
            'pkey': pkey,
            'price_sched': price_adhoc
        }
        ret = self.__cleos.run(
            ['push', 'action', self.__uapp_contract_acc, 'setpriceadh',
             json.dumps(d), '-p', f'{self.__uapp_contract_acc}@modschema'])

        print(ret.stdout)

        return ret

    def set_schema(self, pkey: int, schema):

        d = {
            'pkey': pkey,
            'schema': json.dumps(schema)
        }
        ret = self.__cleos.run(
            ['push', 'action', self.__uapp_contract_acc, 'setchema',
             json.dumps(d), '-p', f'{self.__uapp_contract_acc}@modschema'])

        print(ret.stdout)

        return ret

    def set_rsa_public_key_hash(self, rsa_public_key_hash: str):
        d = {
            'rsa_key': rsa_public_key_hash
        }

        ret = self.__cleos.run(
            ['push', 'action', self.__uapp_contract_acc, 'setrsakey',
             json.dumps(d), '-p', f'{self.__uapp_contract_acc}@modrsakey'])

        print(ret.stdout)

        return ret

    def init_data_request(self, provider_name, schema_id, req_type, price):
        timestamp = unix_timestamp()
        d = {
            'provider_name': provider_name,
            'schema_id': schema_id,
            'ts_created': timestamp,
            'ts_updated': timestamp,
            'req_type': req_type,
            'query': 'test',
            'price': price
        }
        self.__cleos.run(
            ['push', 'action', self.__uapp_contract_acc, 'initreq',
             json.dumps(d), '-p', f'{self.__uapp_contract_acc}@modreq'])

        data_requests = self.get_all_data_requests()
        latest_req_id = list(data_requests.keys())[-1]

        return latest_req_id

    def update_data_request(self, pkey, provider_name, hash, aggr):
        d = {
            'provider_name': provider_name,
            'pkey': pkey,
            'hash': hash,
            'ts_updated': unix_timestamp(),
            'aggr': aggr
        }

        ret = self.__cleos.run(
            ['push', 'action', self.__uapp_contract_acc, 'updatereq',
             json.dumps(d), '-p', f'{provider_name}@modreq'])

        # Todo: Once migrated to EOS RPC API, wait for transaction confirmation
        if ret.stderr.find("executed transaction") != -1:
            ret_list = ret.stderr.split(' ')
            transaction_id = ret_list[2]
            return transaction_id

        return None

    def update_userperms(self, consumer_id, ipfs_hash, merkle_root):
        d = {
            'consumer_id': consumer_id,
            'ipfs_hash': ipfs_hash,
            'merkle_root': merkle_root
        }

        ret = self.__cleos.run(
            ['push', 'action', self.__uapp_contract_acc, 'updateperm',
             json.dumps(d), '-p', f'{self.__uapp_contract_acc}'])

        print(ret)

        # Todo: Once migrated to EOS RPC API, wait for transaction confirmation
        if ret.stderr.find("executed transaction") != -1:
            ret_list = ret.stderr.split(' ')
            transaction_id = ret_list[2]
            return transaction_id

        return None
