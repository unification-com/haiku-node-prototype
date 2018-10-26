import os
import sqlite3
from pathlib import Path


def default_db():
    currentdir = os.path.dirname(os.path.abspath(__file__))
    parentdir = os.path.dirname(currentdir)
    db_path = Path(parentdir + '/dbs/perm_batches.db')
    return str(db_path.resolve())


class PermissionBatcher:

    def __init__(self, db_name: Path):
        self.__db_name = db_name

    def add(self, user_account, consumer_account, op, bc_type='eos'):
        self.__open_con()
        self.__c.execute(f"INSERT INTO permissions "
                         f"VALUES (NULL,"
                         f"'{user_account}', "
                         f"'{consumer_account}',"
                         f"'{op}',"
                         f"0,"
                         f"NULL)")

        self.__conn.commit()

        batch_id = self.__c.lastrowid

        self.__close_con()

        return batch_id

    def get_unprocessed(self):
        self.__open_con()
        self.__c.execute('SELECT * FROM permissions WHERE processed=0 LIMIT 100')
        columns = [d[0] for d in self.__c.description]
        res = [dict(zip(columns, row)) for row in self.__c.fetchall()]

        self.__close_con()

        return res

    def __open_con(self):
        self.__conn = sqlite3.connect(self.__db_name)
        self.__c = self.__conn.cursor()

    def __close_con(self):
        self.__conn.close()
