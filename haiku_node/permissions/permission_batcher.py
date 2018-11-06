import json
import os
import sqlite3
import time
from pathlib import Path


from haiku_node.utils.utils import generate_nonce


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
                         f"NULL,"
                         f"NULL)")

        self.__conn.commit()

        batch_id = self.__c.lastrowid

        self.__close_con()

        return batch_id

    def stash_permission(self, consumer_account, ipfs_hash, merkle_root):
        self.__open_con()
        self.__c.execute(f"INSERT INTO permission_stash "
                         f"VALUES (NULL,"
                         f"'{consumer_account}', "
                         f"'{ipfs_hash}',"
                         f"'{merkle_root}')")

        self.__conn.commit()

        stash_id = self.__c.lastrowid

        self.__close_con()

        return stash_id

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
        from haiku_node.permissions.permissions import UnifPermissions

        batch = self.get_unprocessed(num)
        permissions = UnifPermissions()

        processed = []

        for b in batch:
            perm_obj = {
                'perms': b['perms'],
                'p_nonce': b['p_nonce'],
                'p_sig': b['p_sig'],
                'pub_key': b['pub_key'],
                'schema_id': b['schema_id'],
                'consumer': b['consumer_account'],
                'user': b['end_user_account'],
                'b_nonce': generate_nonce(16),
                'b_time': time.time()
            }
            is_added = permissions.add_update(b['consumer_account'], b['end_user_account'], perm_obj)

            b_proc = {
                'op_id': b['op_id'],
                'consumer': b['consumer_account'],
                'is_added': is_added
            }

            processed.append(b_proc)

        ret_data = permissions.process()

        self.__open_con()
        for b_p in processed:
            if b_p['is_added']:
                ret_d = ret_data[b_p['consumer']]
                if ret_d['bc']:
                    self.__c.execute(f"UPDATE permissions "
                                     f"SET processed='1',"
                                     f"proof_tx='{ret_d['proof_tx']}' "
                                     f"WHERE op_id='{b_p['op_id']}'")
                else:
                    self.__c.execute(f"UPDATE permissions "
                                     f"SET processed='1',"
                                     f"stash_id='{ret_d['stash_id']}' "
                                     f"WHERE op_id='{b_p['op_id']}'")

                self.__conn.commit()
            # Todo - deal with failed operations

        self.__close_con()

        print(ret_data)

    def __open_con(self):
        self.__conn = sqlite3.connect(self.__db_name)
        self.__c = self.__conn.cursor()

    def __close_con(self):
        self.__conn.close()