from haiku_node.lookup.eos_lookup import UnificationLookup

ul = UnificationLookup()

id = ul.get_native_user_id('user2')
eos_acc = ul.get_eos_account(3)
meta_data = ul.get_native_user_meta()
schema_map = ul.get_schema_map('app1.db1')

print("user2 native ID:", id)

print("native UID 3 EOS Account:", eos_acc)

print("Meta data:")

print(meta_data)


print("Schema map for app1.db1:")

print(schema_map)
