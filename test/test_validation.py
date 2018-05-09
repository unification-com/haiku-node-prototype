import os,sys,inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from validation.validation import UnificationACLValidation

v = UnificationACLValidation()
perm = v.app_has_user_permission("unif2", "hodge")

if(perm):
    print("hodge GRANTED permission for unif2 to access data in unif1")
else:
    print("hodge NOT GRANTED permission for unif2 to access data in unif1")

perm = v.app_has_user_permission("unif2", "tester")

if (perm):
    print("tester GRANTED permission for unif2 to access data in unif1")
else:
    print("tester NOT GRANTED permission for unif2 to access data in unif1")

users_granted = v.get_app_allowed_users("unif1")
print("Users who granted permission for unif1:")
print(users_granted)

users_revoked = v.get_app_revoked_users("unif1")
print("Users who revoked permission for unif1:")
print(users_revoked)

users_granted = v.get_app_allowed_users("unif2")
print("Users who granted permission for unif2:")
print(users_granted)

users_revoked = v.get_app_revoked_users("unif2")
print("Users who revoked permission for unif2:")
print(users_revoked)

users_granted = v.get_app_allowed_users("unif3")
print("Users who granted permission for unif3:")
print(users_granted)

users_revoked = v.get_app_revoked_users("unif3")
print("Users who revoked permission for unif3:")
print(users_revoked)

code_valid = v.check_contract_code_hash("unif1", "a2be684581db0f2ff1b14422c9654004e8229d3f11d0507c7918e54fb613cc68")
print("unif1 contract code valid:", code_valid)
