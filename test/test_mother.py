from haiku_node.blockchain.mother import UnificationMother
from haiku_node.config.config import UnificationConfig

apps_to_test = ['app1', 'app2', 'app3']
config = UnificationConfig()
conf = config.get_conf()


def run_test(app):
    global conf

    print("Contacting MOTHER FOR: ", app)

    um = UnificationMother(conf['eos_rpc_ip'], conf['eos_rpc_port'], app)
    print("Valid app: ", um.valid_app())
    print("ACL Hash: ", um.get_hash())
    print("Valid Code: ", um.valid_code())
    print("RPC IP: ", um.get_haiku_rpc_ip())
    print("RPC Port: ", um.get_haiku_rpc_port())
    print("RPC Server: ", um.get_haiku_rpc_server())
    print("Valid DB Schemas: ")
    print(um.get_valid_db_schemas())
    print("-----------------------------------")


if __name__ == '__main__':
    for app in apps_to_test:
        run_test(app)
