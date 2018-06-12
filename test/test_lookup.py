import pytest

from haiku_node.eosio_helpers import eosio_account
from haiku_node.lookup.eos_lookup import UnificationLookup


@pytest.mark.parametrize("app_name", ['app1', 'app2', 'app3'])
def test_validate_lookup_dbs(app_name):
    import sqlite3
    from create_lookups import app_sqlite_target

    db_name = app_sqlite_target(app_name)
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    t = ('user2',)
    c.execute('SELECT native_id FROM lookup WHERE eos_account=?', t)
    res = c.fetchone()[0]
    conn.close()
    assert res == '2'


@pytest.mark.skipif(True, reason="Requires a sqlite database in place")
def test_user_lookup():

    u1name = 15426359793685626880
    u1name_str = '15426359793685626880'
    u1_str = 'user1'
    u1_n_id = 1

    print(f"eosio_account.name_to_string({u1name}) =", eosio_account.name_to_string(u1name))
    print(f"eosio_account.name_to_string('{u1name_str}') =", eosio_account.name_to_string(u1name_str))
    print(f"eosio_account.string_to_name('{u1_str}') =", eosio_account.string_to_name(u1_str))

    assert (eosio_account.name_to_string(u1name) == u1_str) is True
    assert (eosio_account.name_to_string(u1name_str) == u1_str) is True
    assert (eosio_account.string_to_name(u1_str) == u1name) is True

    ul = UnificationLookup()

    print(f"Lookup account as readable string: '{u1_str}'")
    n_id = ul.get_native_user_id(u1_str)
    print(f"{u1_str} native ID:", n_id)

    assert (int(n_id) == u1_n_id) is True

    print(f"Lookup account as account_name int: {u1name}")
    n_id = ul.get_native_user_id(u1name)
    print(f"{u1_str} native ID:", n_id)

    assert (int(n_id) == u1_n_id) is True

    print(f"Lookup account as account_name string: '{u1name_str}'")
    n_id = ul.get_native_user_id(u1name_str)
    print(f"{u1_str} native ID:", n_id)

    assert (int(n_id) == u1_n_id) is True

    print(f"Lookup native UID {u1_n_id} as EOS Account")
    eos_acc = ul.get_eos_account(u1_n_id)
    print(f"UID {u1_n_id} EOS account:", eos_acc)

    assert (eos_acc == u1_str) is True

    meta_data = ul.get_native_user_meta()
    print("Meta data:")
    print(meta_data)

    schema_map = ul.get_schema_map('app1.db1')
    print("Schema map for app1.db1:")

    print(schema_map)

    real_table = ul.get_real_table_info('app1.db1', 'data_1')
    print("real table data for app1.db1, data_1:")
    print(real_table)


if __name__ == "__main__":
    test_user_lookup()
