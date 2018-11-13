import os
import sqlite3

from pathlib import Path

import logging

log = logging.getLogger(__name__)

usernames = ['user1', 'user2', 'user3']


def test_root() -> Path:
    return Path(os.path.dirname(os.path.abspath(__file__)))


def app_sqlite_target(user_name: str) -> Path:
    db_path = Path(test_root() / Path(
        f'data/babel_db/{user_name}.babel.db'))
    return db_path.resolve()


def create_babel_db(user_name: str):

    log.info(f'Create {user_name} BABEL DB')
    db_name = app_sqlite_target(user_name)

    log.info(f"create db: {db_name}")

    if os.path.exists(db_name):
        log.info(f"{db_name} exists. Delete")
        os.unlink(db_name)

    _create_babel_db(db_name)


def _create_babel_db(db_name: Path):
    conn = sqlite3.connect(str(db_name))
    c = conn.cursor()
    c.execute('''CREATE TABLE perm_change_requests (req_id INTEGER PRIMARY KEY, 
                 end_user_account text, 
                 provider_account text,
                 consumer_account text, 
                 schema_id text,
                 perms text,
                 p_nonce text,
                 p_sig text,
                 pub_key text,
                 processed INTEGER,
                 proof_tx text NULL,
                 provider_process_id INTEGER NULL)''')
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

    for user in usernames:
        create_babel_db(user)
