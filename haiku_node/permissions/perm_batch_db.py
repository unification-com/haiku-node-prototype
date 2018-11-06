import os
import sqlite3

from pathlib import Path


def default_db():
    currentdir = os.path.dirname(os.path.abspath(__file__))
    parentdir = os.path.dirname(currentdir)
    db_path = Path(parentdir + '/dbs/perm_batches.db')
    return str(db_path.resolve())


class PermissionBatchDatabase:
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

    def update_processed(self, op_id, stash_id=None, proof_tx=None):
        self.__open_con()

        if proof_tx is not None:
            self.__c.execute(f"UPDATE permissions "
                             f"SET processed='1',"
                             f"proof_tx='{proof_tx}' "
                             f"WHERE op_id='{op_id}'")
        elif stash_id is not None:
            self.__c.execute(f"UPDATE permissions "
                             f"SET processed='1',"
                             f"stash_id='{stash_id}' "
                             f"WHERE op_id='{op_id}'")
        else:
            print("nowt")

        self.__conn.commit()
        self.__close_con()

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

    def delete_op(self, op_id):
        self.__open_con()

        self.__c.execute(f"DELETE FROM permissions "
                         f"WHERE op_id='{op_id}'")

        self.__conn.commit()
        self.__close_con()

    def get_latest_stash(self, consumer_account):
        stash = {}
        self.__open_con()
        self.__c.execute(f'SELECT * FROM permission_stash '
                         f"WHERE consumer_account='{consumer_account}'"
                         f'ORDER BY stash_id DESC '
                         f'LIMIT 1')
        columns = [d[0] for d in self.__c.description]
        res = [dict(zip(columns, row)) for row in self.__c.fetchall()]

        self.__close_con()

        if res:
            stash = res[0]

        return stash

    def __open_con(self):
        self.__conn = sqlite3.connect(self.__db_name)
        self.__c = self.__conn.cursor()

    def __close_con(self):
        self.__conn.close()
