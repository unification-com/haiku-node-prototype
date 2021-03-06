import pytest
import os

from haiku_node.data.factory import UnificationDataFactory
from haiku_node.config.config import UnificationConfig
from eosapi import Client


@pytest.mark.skipif(
    True, reason="Requires a running EOS node, hence is not a unit test")
def test_data_factory():
    conf = UnificationConfig()
    eos_client = Client(
        nodes=[f"{conf['eos_rpc_ip']}:{conf['eos_rpc_port']}"])

    print("Bulk data request from app3")
    data_factory = UnificationDataFactory(eos_client, os.environ['app_name'], 'app3')
    # encrypted_data = data_factory.get_encrypted_data()
    raw_data = data_factory.get_raw_data()

    print(raw_data[:50])
    # print(encrypted_data[:50])

    print("request from app3 for user1's data")
    data_factory = UnificationDataFactory(eos_client, os.environ['app_name'], 'app3', ['user1'])
    # encrypted_data = data_factory.get_encrypted_data()
    raw_data = data_factory.get_raw_data()

    print(raw_data[:50])
    # print(encrypted_data[:50])


if __name__ == "__main__":
    test_data_factory()
