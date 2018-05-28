from eosapi import Client

from haiku_node.blockchain.acl import UnificationACL
from haiku_node.blockchain.mother import UnificationMother
from haiku_node.config.config import UnificationConfig

apps_to_test = ['app1', 'app2', 'app3']
config = UnificationConfig()


def run_test(app):
    print("Loading ACL/Meta Contract for: ", app)

    eos_client = Client(
        nodes=[f"http://{config['eos_rpc_ip']}:{config['eos_rpc_port']}"])
    u_acl = UnificationACL(eos_client, app)

    print("Data Schemas in Contract:")
    print(u_acl.get_db_schemas())
    print("Data Sources:")
    print(u_acl.get_data_sources())

    print("Current VALID Schema(s), as per MOTHER:")
    um = UnificationMother(eos_client, app)
    for sn, sv in um.get_valid_db_schemas().items():
        print(u_acl.get_current_valid_schema(sn, sv))

    print("Check Permissions")
    for req_app in apps_to_test:
        print("Check perms for Requesting App: ", req_app)
        granted, revoked = u_acl.get_perms_for_req_app(req_app)
        print("Users who Granted:")
        print(granted)
        print("Users who Revoked:")
        print(revoked)

    print("-----------------------------------")


if __name__ == '__main__':
    for app in apps_to_test:
        run_test(app)
