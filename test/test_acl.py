from eosapi import Client

from haiku_node.blockchain.uapp import UnificationUapp
from haiku_node.config.config import UnificationConfig

apps_to_test = ['app1', 'app2', 'app3']
config = UnificationConfig()


def run_test(app):
    print("Loading ACL/Meta Contract for: ", app)

    eos_client = Client(
        nodes=[f"http://{config['eos_rpc_ip']}:{config['eos_rpc_port']}"])
    uapp_sc = UnificationUapp(eos_client, app)

    print("Data Schemas in Contract:")
    print(uapp_sc.get_all_db_schemas())

    print("Check Permissions")
    for req_app in apps_to_test:
        print("Check perms for Requesting App: ", req_app)
        granted, revoked = uapp_sc.get_perms_for_req_app(req_app)
        print("Users who Granted:")
        print(granted)
        print("Users who Revoked:")
        print(revoked)

    print("-----------------------------------")


if __name__ == '__main__':
    for app in apps_to_test:
        run_test(app)
