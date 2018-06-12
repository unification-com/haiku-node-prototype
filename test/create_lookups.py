import json
import os
import sqlite3

from pathlib import Path

import logging

log = logging.getLogger(__name__)

appnames = ['app1', 'app2', 'app3']


def test_root():
    return Path(os.path.dirname(os.path.abspath(__file__)))


def get_demo_config():
    demo_config = Path(test_root() / Path('data/demo_config.json'))
    return json.loads(demo_config.read_text())


def target_file(app_name):
    db_path = Path(test_root() / Path(
        f'data/lookups/{app_name}.unification_lookup.db'))
    return str(db_path.resolve())


def create_lookup_db(app):
    demo_config = get_demo_config()
    demo_apps = demo_config['demo_apps']
    app_conf = demo_apps[app]

    log.info(f'Create {app} Lookup')
    db_name = target_file(app)

    log.info(f"create db: {db_name}")

    if os.path.exists(db_name):
        log.info(f"{db_name} exists. Delete")
        os.unlink(db_name)

    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute('''CREATE TABLE lookup (native_id text, eos_account text)''')
    c.execute('''CREATE TABLE lookup_meta (native_table text, native_field text, field_type text)''')
    c.execute('''CREATE TABLE schema_map (sc_schema_name text, native_db text, native_db_platform text)''')
    c.execute('''CREATE TABLE table_maps (sc_schema_name text, sc_table_name text, real_table_name text, user_id_column text)''')

    c.execute(f"INSERT INTO lookup_meta VALUES ('{app_conf['lookup']['lookup_meta']['native_table']}', "
              f"'{app_conf['lookup']['lookup_meta']['native_field']}', "
              f"'{app_conf['lookup']['lookup_meta']['field_type']}')")

    for u in app_conf['lookup']['lookup_users']:
        c.execute(f"INSERT INTO lookup VALUES ('{u['native_id']}', '{u['eos_account']}')")

    for sc in app_conf['db_schemas']:
        c.execute(f"INSERT INTO schema_map VALUES ('{sc['schema_name']}', '{sc['database']}', '{sc['db_platform']}')")

        for tm in sc['table_maps']:
            c.execute(
                f"INSERT INTO table_maps VALUES ('{sc['schema_name']}', '{tm['schema_table_id']}', "
                f"'{tm['db_table']}', '{tm['user_id_column']}')")

    conn.commit()
    conn.close()

    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    log.info('Test user2 == 2')
    t = ('user2',)
    c.execute('SELECT native_id FROM lookup WHERE eos_account=?', t)
    res = c.fetchone()[0]
    log.info(f"user2 native ID: {res}")

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
        create_lookup_db(app)
