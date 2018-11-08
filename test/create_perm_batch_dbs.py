import os
import sqlite3

from pathlib import Path

import logging

log = logging.getLogger(__name__)

appnames = ['app1', 'app2', 'app3']


def test_root() -> Path:
    return Path(os.path.dirname(os.path.abspath(__file__)))


def app_sqlite_target(app_name: str) -> Path:
    db_path = Path(test_root() / Path(
        f'data/perm_batch/{app_name}.perm_batches.db'))
    return db_path.resolve()


def create_perm_batch_db(app_name: str):

    log.info(f'Create {app_name} Permission Batch DB')
    db_name = app_sqlite_target(app_name)

    log.info(f"create db: {db_name}")

    if os.path.exists(db_name):
        log.info(f"{db_name} exists. Delete")
        os.unlink(db_name)

    _create_perm_batch_db(db_name)


def _create_perm_batch_db(db_name: Path):
    conn = sqlite3.connect(str(db_name))
    c = conn.cursor()
    c.execute('''CREATE TABLE permissions (op_id INTEGER PRIMARY KEY, 
                 end_user_account text, 
                 consumer_account text, 
                 schema_id text,
                 perms text,
                 p_nonce text,
                 p_sig text,
                 pub_key text,
                 processed INTEGER,
                 proof_tx text NULL,
                 stash_id INTEGER NULL)''')
    conn.commit()
    c.execute('''CREATE TABLE permission_stash (stash_id INTEGER PRIMARY KEY,
                 consumer_account text,
                 ipfs_hash text,
                 merkle_root text)''')
    conn.commit()
    conn.close()


def configure_logging():
    log.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    log.addHandler(ch)


if __name__ == "__main__":
    configure_logging()

    for app in appnames:
        create_perm_batch_db(app)
