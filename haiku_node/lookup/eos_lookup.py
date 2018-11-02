import os
import sqlite3
from pathlib import Path

from haiku_node.blockchain_helpers.eos import eosio_account


def default_db():
    currentdir = os.path.dirname(os.path.abspath(__file__))
    parentdir = os.path.dirname(currentdir)
    db_path = Path(parentdir + '/dbs/unification_lookup.db')
    return str(db_path.resolve())


class UnificationLookup:

    def __init__(self, db_name: Path):
        self.__db_name = db_name

    def get_native_user_id(self, account_name):

        if isinstance(account_name, int):
            account_name = eosio_account.name_to_string(account_name)
        elif isinstance(account_name, str) and account_name.isdigit():
            account_name = eosio_account.name_to_string(account_name)

        self.__open_con()
        t = (account_name,)
        self.__c.execute('SELECT native_id FROM lookup WHERE eos_account=?', t)

        res = self.__c.fetchone()[0]

        self.__close_con()

        return res

    def get_eos_account(self, native_id):
        self.__open_con()
        t = (native_id,)
        self.__c.execute('SELECT eos_account FROM lookup WHERE native_id=?', t)

        res = self.__c.fetchone()[0]

        self.__close_con()

        return res

    def get_native_user_meta(self):
        self.__open_con()
        self.__c.execute('SELECT * FROM lookup_meta WHERE 1')
        res = self.__c.fetchone()

        dt = {
            'table': res[0],
            'field': res[1],
            'type': res[2]
        }

        self.__close_con()

        return dt

    def get_schema_map(self, sc_schema_pkey):
        self.__open_con()
        t = (sc_schema_pkey,)
        self.__c.execute('SELECT * FROM schema_map WHERE sc_schema_pkey=?', t)

        res = self.__c.fetchone()

        dt = {
            'sc_schema_pkey': res[0],
            'db_name': res[1],
            'db_platform': res[2]
        }

        self.__close_con()

        return dt

    def get_real_table_info(self, sc_schema_pkey, sc_table_name):
        self.__open_con()
        t = (sc_schema_pkey, sc_table_name)
        self.__c.execute('SELECT * FROM table_maps WHERE sc_schema_pkey=? AND '
                         'sc_table_name=?', t)

        res = self.__c.fetchone()

        dt = {
            'sc_schema_pkey': res[0],
            'sc_table_name': res[1],
            'real_table_name': res[2],
            'user_id_column': res[3]
        }

        self.__close_con()

        return dt

    def __open_con(self):
        self.__conn = sqlite3.connect(self.__db_name)
        self.__c = self.__conn.cursor()

    def __close_con(self):
        self.__conn.close()
