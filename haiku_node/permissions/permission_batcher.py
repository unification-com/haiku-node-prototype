import json
import os
import sqlite3
from pathlib import Path

from haiku_node.permissions.permissions import UnifPermissions


def default_db():
    currentdir = os.path.dirname(os.path.abspath(__file__))
    parentdir = os.path.dirname(currentdir)
    db_path = Path(parentdir + '/dbs/perm_batches.db')
    return str(db_path.resolve())


class PermissionBatcher:

    def __init__(self, db_name: Path):
        self.__db_name = db_name

    def add(self, user_account, consumer_account, schema_id, perms, p_nonce, p_sig, pub_key, bc_type='eos'):
        self.__open_con()
        self.__c.execute(f"INSERT INTO permissions "
                         f"VALUES (NULL,"
                         f"'{user_account}', "
                         f"'{consumer_account}',"
                         f"'{schema_id}',"
                         f"'{perms}',"
                         f"'{p_nonce}',"
                         f"'{p_sig}',"
                         f"'{pub_key}',"
                         f"0,"
                         f"NULL)")

        self.__conn.commit()

        batch_id = self.__c.lastrowid

        self.__close_con()

        return batch_id

    def get_unprocessed(self, num=10):
        self.__open_con()
        self.__c.execute(f'SELECT * FROM permissions '
                         f'WHERE processed=0 '
                         f'ORDER BY consumer_account ASC '
                         f'LIMIT {num}')
        columns = [d[0] for d in self.__c.description]
        res = [dict(zip(columns, row)) for row in self.__c.fetchall()]

        self.__close_con()

        return res

    def process_batch(self, num=10):
        batch = self.get_unprocessed(num)
        permissions = UnifPermissions()

        for b in batch:
            perm_obj = {
                'perms': b['perms'],
                'p_nonce': b['p_nonce'],
                'p_sig': b['p_sig'],
                'pub_key': b['pub_key'],
                'schema_id': b['schema_id'],
                'consumer': b['consumer_account'],
                'user': b['end_user_account']
            }
            permissions.add_update(b['consumer_account'], b['end_user_account'], perm_obj)

        permissions.process()

    def __open_con(self):
        self.__conn = sqlite3.connect(self.__db_name)
        self.__c = self.__conn.cursor()

    def __close_con(self):
        self.__conn.close()
