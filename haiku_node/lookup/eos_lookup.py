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

    def create_db(self):
        # TODO: Migrate to create_accounts.py or similar init script
        # save locally in each app's container, with app specific data
        self.__open_con()
        self.__c.execute('''CREATE TABLE lookup
                     (native_id text, eos_account text)''')

        self.__c.execute('''CREATE TABLE lookup_meta
                             (native_table text, native_field text, field_type text)''')

        self.__c.execute("INSERT INTO lookup_meta VALUES ('Users','ID','int')")

        self.__c.execute("INSERT INTO lookup VALUES ('1', 'user1')")
        self.__c.execute("INSERT INTO lookup VALUES ('2', 'user2')")
        self.__c.execute("INSERT INTO lookup VALUES ('3', 'user3')")

        self.__conn.commit()
        self.__close_con()

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

    def __open_con(self):
        self.__conn = sqlite3.connect(self.__db_name)
        self.__c = self.__conn.cursor()

    def __close_con(self):
        self.__conn.close()