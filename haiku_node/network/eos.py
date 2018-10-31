import os

from enum import Enum

from eosapi import Client

from haiku_node.blockchain.ipfs import IPFSDataStore
from haiku_node.blockchain_helpers.eosio_cleos import EosioCleos
from haiku_node.config.config import UnificationConfig


class Environment(Enum):
    TARGET = 1
    CONTAINER = 2
    HOST = 3
    UNITTEST = 4


def get_enum():
    haiku_env = os.environ.get('haiku_env')
    if haiku_env is None:
        return Environment.TARGET
    else:
        if haiku_env == 'container':
            return Environment.CONTAINER
        if haiku_env == 'host':
            return Environment.HOST

        raise Exception(f'Unhandled host environment {haiku_env}')


def get_cleos():
    haiku_env = get_enum()

    if haiku_env == Environment.HOST:
        cleos = EosioCleos(host=True)
    else:
        cleos = EosioCleos(host=False)
    return cleos


def get_eos_rpc_client():
    haiku_env = get_enum()

    conf = UnificationConfig()

    if haiku_env == Environment.HOST:
        eos_host = '127.0.0.1'
        eos_port = '8888'
    else:
        eos_host = conf['eos_rpc_ip']
        eos_port = conf['eos_rpc_port']

    return Client(nodes=[f"http://{eos_host}:{eos_port}"])


def get_ipfs_client():
    """
    #TODO: This method does not belong here
    """
    haiku_env = get_enum()

    if haiku_env == Environment.HOST:
        return IPFSDataStore(host='127.0.0.1')
    else:
        return IPFSDataStore()
