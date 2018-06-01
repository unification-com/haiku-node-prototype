import pytest

from haiku_node.data.factory import UnificationDataFactory
from haiku_node.config.config import UnificationConfig
from eosapi import Client

@pytest.mark.skipif(True, reason="requires test setup")
def test_data_factory():
    conf = UnificationConfig()
    eos_client = Client(
        nodes=[f"{conf['eos_rpc_ip']}:{conf['eos_rpc_port']}"])

    print("Bulk request")
    data_factory = UnificationDataFactory(eos_client, 'app1', 'app2')
    encrypted_data = data_factory.get_encrypted_data()
    raw_data = data_factory.get_raw_data()

    print(raw_data)
    print(encrypted_data)

    print("request for user1's data")
    data_factory = UnificationDataFactory(eos_client, 'app1', 'app2', ['user1'])
    encrypted_data = data_factory.get_encrypted_data()
    raw_data = data_factory.get_raw_data()

    print(raw_data)
    print(encrypted_data)


if __name__ == "__main__":
    test_data_factory()