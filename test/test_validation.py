import os,sys,inspect,json

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from validation.validation import UnificationACLValidation

#get requesting app
requesting_app = sys.argv[1]

#list of users to test - EOS account names.
users_to_test = ["user1", "user2", "user3"]

with open(parentdir + '/config/config.json') as f:
    conf = json.load(f)

print("THIS app is", conf['acl_contract'])

v = UnificationACLValidation(requesting_app)

app_valid = v.valid_app()
print("Requesting App", requesting_app, "Valid according to MOTHER: ", app_valid)

code_valid = v.valid_code()
print(requesting_app, "contract code hash valid:", code_valid)

if app_valid and code_valid:

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
            print(user, "NOT GRANTED permission for ", requesting_app, " to access data in", conf['acl_contract'])

else:
    if app_valid is False:
        print("App ont valid according to MOTHER")
    if code_valid is False:
        print("Code hash did not match hash held by MOTHER")
