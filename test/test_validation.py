import os,sys,inspect,json

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from validation.validation import UnificationACLValidation

requesting_app = sys.argv[1]

with open(parentdir + '/config/config.json') as f:
    conf = json.load(f)

print("THIS app is",conf['acl_contract'])

v = UnificationACLValidation(requesting_app)

print("Requesting App", requesting_app, "Valid accoring to MOTHER: ", v.valid_app())

users_granted = v.users_granted()
print("Users who granted permission for:", requesting_app)
print(users_granted)

users_revoked = v.users_revoked()
print("Users who revoked permission for:", requesting_app)
print(users_revoked)

user = "user1"
perm = v.app_has_user_permission(user)
if(perm):
    print(user, "GRANTED permission for", requesting_app, "to access data in", conf['acl_contract'])
else:
    print(user, "NOT GRANTED permission for ", requesting_app, " to access data in", conf['acl_contract'])

user = "user2"
perm = v.app_has_user_permission(user)
if(perm):
    print(user, "GRANTED permission for", requesting_app, "to access data in", conf['acl_contract'])
else:
    print(user, "NOT GRANTED permission for", requesting_app, "to access data in", conf['acl_contract'])

user = "user3"
perm = v.app_has_user_permission(user)
if (perm):
    print(user, "GRANTED permission for", requesting_app, "to access data in", conf['acl_contract'])
else:
    print(user, "NOT GRANTED permission for", requesting_app, "to access data in", conf['acl_contract'])


#code_valid = v.check_contract_code_hash("unif1", "a2be684581db0f2ff1b14422c9654004e8229d3f11d0507c7918e54fb613cc68")
#print("unif1 contract code valid:", code_valid)
