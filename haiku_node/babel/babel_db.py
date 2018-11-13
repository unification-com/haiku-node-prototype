import os
import sqlite3

from pathlib import Path


def default_db(user) -> Path:
    currentdir = os.path.dirname(os.path.abspath(__file__))
    parentdir = os.path.dirname(currentdir)
    db_path = Path(parentdir + f'/dbs/{user}.babel.db')
    return db_path.resolve()


class BabelDatabase:
    def __init__(self, db_name: Path):
        self.__db_name = db_name

    def add_change_request(self, user_account, provider_account, consumer_account,
                           schema_id, perms, p_nonce, p_sig, public_key):
        self.__open_con()
        self.__c.execute(f"INSERT INTO perm_change_requests "
                         f"VALUES (NULL,"
                         f"'{user_account}', "
                         f"'{provider_account}', "
                         f"'{consumer_account}',"
                         f"'{schema_id}',"
                         f"'{perms}',"
                         f"'{p_nonce}',"
                         f"'{p_sig}',"
                         f"'{public_key}',"
                         f"0,"
                         f"NULL,"
                         f"NULL)")

        self.__conn.commit()

        request_id = self.__c.lastrowid

        self.__close_con()

        return request_id

    def update_provider_process_id(self, request_id, provider_process_id):
        self.__open_con()

        self.__c.execute(f"UPDATE perm_change_requests "
                         f"SET provider_process_id='{provider_process_id}' "
                         f"WHERE req_id='{request_id}'")

        self.__conn.commit()
        self.__close_con()

    def update_processed(self, request_id, proof_tx=None):
        self.__open_con()

        self.__c.execute(f"UPDATE perm_change_requests "
                         f"SET processed='1',"
                         f"proof_tx='{proof_tx}' "
                         f"WHERE req_id='{request_id}'")

        self.__conn.commit()
        self.__close_con()

    def get_unprocessed(self, num=10):
        self.__open_con()
        self.__c.execute(f'SELECT * FROM perm_change_requests '
                         f'WHERE processed=0 '
                         f'LIMIT {num}')
        columns = [d[0] for d in self.__c.description]
        res = [dict(zip(columns, row)) for row in self.__c.fetchall()]

        self.__close_con()

        return res

    def get_request_by_id(self, request_id, user_account):
        op_data = None
        self.__open_con()
        self.__c.execute(f'SELECT * FROM perm_change_requests '
                         f"WHERE req_id='{request_id}' "
                         f"AND end_user_account='{user_account}' "
                         f'LIMIT 1')
        columns = [d[0] for d in self.__c.description]
        res = [dict(zip(columns, row)) for row in self.__c.fetchall()]

        self.__close_con()

        if res:
            op_data = res[0]

        return op_data

    def __open_con(self):
        self.__conn = sqlite3.connect(str(self.__db_name))
        self.__c = self.__conn.cursor()

    def __close_con(self):
        self.__conn.close()
