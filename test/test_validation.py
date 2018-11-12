import sys

from eosapi import Client

from haiku_node.config.config import UnificationConfig
from haiku_node.blockchain_helpers.eos import eosio_account
from haiku_node.validation.validation import UnificationAppScValidation


def run_test(requesting_app):

    conf = UnificationConfig()
    eos_client = Client(
        nodes=[f"http://{conf['eos_rpc_ip']}:{conf['eos_rpc_port']}"])

    print("THIS app is", conf['acl_contract'])

    v = UnificationAppScValidation(
        eos_client, conf['acl_contract'], requesting_app)

    app_valid = v.valid_app()
    print(f"Requesting App {requesting_app} Valid according to MOTHER: "
          f"{app_valid}")

    code_valid = v.valid_code()
    print(requesting_app, "contract code hash valid:", code_valid)

    both_valid = v.valid()
    print(requesting_app, "is considered valid:", both_valid)

    if both_valid:

        print("App valid according to MOTHER. App code hash valid.")

    else:
        if app_valid is False:
            print("App not valid according to MOTHER")
        if code_valid is False:
            print("Code hash did not match hash held by MOTHER")


if __name__ == '__main__':
    # get requesting app
    if len(sys.argv) > 1:
        requesting_app = sys.argv[1]
        run_test(requesting_app)

        u = "user.1"
        n = eosio_account.string_to_name(u)
        account_name = eosio_account.name_to_string(n)
        print("str", account_name)

    else:
        print("run with requesting app account as arg1, e.g.:")
        print("python test_validation.py app2")
