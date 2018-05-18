import os,sys,inspect
from haiku_node.validation.validation import UnificationAppScValidation
from haiku_node.config.config import UnificationConfig
from haiku_node.eosio_helpers import eosio_account

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)


def run_test(requesting_app):
    #list of users to test - EOS account names.
    users_to_test = ["user1", "user2", "user3"]

    config = UnificationConfig()
    conf = config.get_conf()

    print("THIS app is", conf['acl_contract'])

    v = UnificationAppScValidation(conf, requesting_app)

    app_valid = v.valid_app()
    print("Requesting App", requesting_app, "Valid according to MOTHER: ", app_valid)

    code_valid = v.valid_code()
    print(requesting_app, "contract code hash valid:", code_valid)

    both_valid = v.valid()
    print(requesting_app, "is considered valid:", both_valid)

    if both_valid:

        print("App valid according to MOTHER. App code hash valid. Check user permissions.")

        users_granted = v.users_granted()
        print("Users who granted permission for:", requesting_app)
        print(users_granted)

        users_revoked = v.users_revoked()
        print("Users who revoked permission for:", requesting_app)
        print(users_revoked)

        for user in users_to_test:
            perm = v.app_has_user_permission(user)
            if (perm):
                print(user, "GRANTED permission for", requesting_app, "to access data in", conf['acl_contract'])
            else:
                print(user, "NOT GRANTED permission for", requesting_app, "to access data in", conf['acl_contract'])

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
        str = eosio_account.name_to_string(n)
        print("str", str)

    else:
        print("run with requesting app account as arg1, e.g.:")
        print("python test_validation.py app2")
