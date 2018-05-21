import os, inspect
import sqlite3
from pathlib import Path


class UnificationLookup:

    def __init__(self):
        currentdir = os.path.dirname(
            os.path.abspath(inspect.getfile(inspect.currentframe())))
        parentdir = os.path.dirname(currentdir)
        db_path = Path(parentdir + '/lookup/unification_lookup.db')
        self.__db_name = str(db_path.resolve())

    def get_native_user_id(self, account_name):
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

    def get_native_meta(self):
        self.__open_con()
        self.__c.execute('SELECT * FROM lookup_meta WHERE 1')
        res = self.__c.fetchone()

        dt = {}
        dt['table'] = res[0]
        dt['field'] = res[1]
        dt['type'] = res[2]

        self.__close_con()

        return dt

    def get_schema_map(self,account_name):
        self.__open_con()
        t = (account_name,)
        self.__c.execute('SELECT * FROM schema_map WHERE sc_schema_name=?', t)

        res = self.__c.fetchone()

        dt = {}
        dt['sc_schema_name'] = res[0]
        dt['db_name'] = res[1]
        dt['db_platform'] = res[2]

        self.__close_con()

        return dt

    def __open_con(self):
        self.__conn = sqlite3.connect(self.__db_name)
        self.__c = self.__conn.cursor()

    def __close_con(self):
        self.__conn.close()