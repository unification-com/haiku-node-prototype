from haiku_node.lookup.eos_lookup import UnificationLookup

ul = UnificationLookup()

id = ul.get_native_user_id('user2')
eos_acc = ul.get_eos_account(3)

print("user2 native ID:", id)

print("native UID 3 EOS Account:", eos_acc)
