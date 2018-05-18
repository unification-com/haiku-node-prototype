from haiku_node.blockchain.acl import UnificationACL
from haiku_node.config.config import UnificationConfig

apps_to_test = ['app1', 'app2', 'app3']
config = UnificationConfig()
conf = config.get_conf()


def run_test(app):
    global conf

    print("Loading ACL/Meta Contract for: ", app)

    u_acl = UnificationACL(conf['eos_rpc_ip'], conf['eos_rpc_port'], app)

    print("Data Schemas:")
    print(u_acl.get_db_schemas())
    print("Data Sources:")
    print(u_acl.get_data_sources())

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
