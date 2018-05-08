from validation.validation import UnificationACLValidation

v = UnificationACLValidation()
perm = v.app_has_user_permission("unif2", "hodge")

if(perm):
    print("hodge GRANTED")
else:
    print("hodge NOT GRANTED")

perm = v.app_has_user_permission("unif2", "tester")

if (perm):
    print("tester GRANTED")
else:
    print("tester NOT GRANTED")

perm = v.app_has_user_permission("unif2", "user1")

if(perm):
    print("user1 GRANTED")
else:
    print("user1 NOT GRANTED")

perm = v.app_has_user_permission("unif2", "user2")

if(perm):
    print("user2 GRANTED")
else:
    print("user2 NOT GRANTED")

perm = v.app_has_user_permission("unif2", "user3")

if(perm):
    print("user3 GRANTED")
else:
    print("user3 NOT GRANTED")

users_granted = v.get_app_allowed_users("unif2");
print("Users who granted permission for unif2:")
print(users_granted)

users_revoked = v.get_app_revoked_users("unif2");
print("Users who revoked permission for unif2:")
print(users_revoked)

users_granted = v.get_app_allowed_users("unif3");
print("Users who granted permission for unif3:")
print(users_granted)

users_revoked = v.get_app_revoked_users("unif3");
print("Users who revoked permission for unif3:")
print(users_revoked)