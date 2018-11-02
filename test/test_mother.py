import json
from pathlib import Path

from haiku_node.blockchain.eos.mother import UnificationMother
from haiku_node.config.config import UnificationConfig
from haiku_node.network.eos import get_cleos, get_eos_rpc_client

apps_to_test = ['app1', 'app2', 'app3']
config = UnificationConfig()

demo_config = json.loads(Path('test/data/demo_config.json').read_text())
demo_apps = demo_config["demo_apps"]


def run_test(app):
    print("Contacting MOTHER FOR: ", app)
    eos_client = get_eos_rpc_client()
    um = UnificationMother(eos_client, app, get_cleos())
    print("Valid app: ", um.valid_app())
    assert um.valid_app() is True

    print("ACL Hash in MOTHER: ", um.get_hash_in_mother())
    print("Deployed ACL Contract hash: ", um.get_deployed_contract_hash())
    assert um.get_hash_in_mother() == um.get_deployed_contract_hash()

    print("Valid Code: ", um.valid_code())
    assert um.valid_code() is True

    print("RPC IP: ", um.get_haiku_rpc_ip())
    assert um.get_haiku_rpc_ip() == demo_apps[app]['rpc_server']

    print("RPC Port: ", um.get_haiku_rpc_port())
    assert int(um.get_haiku_rpc_port()) == int(
        demo_apps[app]['rpc_server_port'])

    print("RPC Server: ", um.get_haiku_rpc_server())
    print("-----------------------------------")


if __name__ == '__main__':
    for app in apps_to_test:
        run_test(app)
