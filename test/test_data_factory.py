from haiku_node.data.factory import UnificationDataFactory
from haiku_node.config.config import UnificationConfig
from eosapi import Client


def test_data_factory():
    conf = UnificationConfig()
    eos_client = Client(
        nodes=[f"http://127.0.0.1:{conf['eos_rpc_port']}"])
    data_factory = UnificationDataFactory(eos_client, 'app1', 'app2')

    print("Bulk request")
    encrypted_data = data_factory.get_data()
    print(encrypted_data)

    print("request for user1's data")
    encrypted_data = data_factory.get_data(['user1'])

    print(encrypted_data)


if __name__ == "__main__":
    test_data_factory()