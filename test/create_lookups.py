import os, inspect
import json
import sqlite3
from pathlib import Path
import logging

log = logging.getLogger(__name__)
currentdir = os.path.dirname(
            os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
app_config = json.loads(Path(parentdir + '/test/data/test_apps.json').read_text())


def create_app1():
    global app_config
    app_conf = app_config['app1']

    log.info('Create App1 Lookup')
    currentdir = os.path.dirname(
        os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    db_path = Path(parentdir + '/test/data/app1_unification_lookup.db')
    db_name = str(db_path.resolve())

    log.info(db_name)

    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute('''CREATE TABLE lookup
                         (native_id text, eos_account text)''')

    c.execute('''CREATE TABLE lookup_meta
                                 (native_table text, native_field text, field_type text)''')

    c.execute('''CREATE TABLE schema_map
                                     (sc_schema_name text, native_db text, native_db_platform text)''')

    c.execute("INSERT INTO lookup_meta VALUES ('Users','ID','int')")

    c.execute("INSERT INTO lookup VALUES ('1', 'user1')")
    c.execute("INSERT INTO lookup VALUES ('2', 'user2')")
    c.execute("INSERT INTO lookup VALUES ('3', 'user3')")

    for i in app_conf['db_schemas']:
        c.execute(f"INSERT INTO schema_map VALUES ('{i['schema_name']}', '{i['database']}', '{i['db_platform']}')")

    conn.commit()
    conn.close()

    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    log.info('Test user2 == 2')
    t = ('user2',)
    c.execute('SELECT native_id FROM lookup WHERE eos_account=?', t)
    res = c.fetchone()[0]
    print("user2 native ID:", res)

    conn.close()


def create_app2():
    global app_config
    app_conf = app_config['app2']

    log.info('Create App2 Lookup')
    currentdir = os.path.dirname(
        os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    db_path = Path(parentdir + '/test/data/app2_unification_lookup.db')
    db_name = str(db_path.resolve())

    log.info(db_name)

    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute('''CREATE TABLE lookup
                         (native_id text, eos_account text)''')

    c.execute('''CREATE TABLE lookup_meta
                                 (native_table text, native_field text, field_type text)''')

    c.execute('''CREATE TABLE schema_map
                                     (sc_schema_name text, native_db text, native_db_platform text)''')

    c.execute("INSERT INTO lookup_meta VALUES ('People','PeopleID','int')")

    c.execute("INSERT INTO lookup VALUES ('1', 'user1')")
    c.execute("INSERT INTO lookup VALUES ('2', 'user2')")
    c.execute("INSERT INTO lookup VALUES ('3', 'user3')")

    for i in app_conf['db_schemas']:
        c.execute(f"INSERT INTO schema_map VALUES ('{i['schema_name']}', '{i['database']}', '{i['db_platform']}')")

    conn.commit()
    conn.close()

    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    log.info('Test user2 == 2')
    t = ('user2',)
    c.execute('SELECT native_id FROM lookup WHERE eos_account=?', t)
    res = c.fetchone()[0]
    print("user2 native ID:", res)

    conn.close()


def create_app3():
    global app_config
    app_conf = app_config['app2']

    log.info('Create App3 Lookup')
    currentdir = os.path.dirname(
        os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    db_path = Path(parentdir + '/test/data/app3_unification_lookup.db')
    db_name = str(db_path.resolve())

    log.info(db_name)

    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute('''CREATE TABLE lookup
                         (native_id text, eos_account text)''')

    c.execute('''CREATE TABLE lookup_meta
                                 (native_table text, native_field text, field_type text)''')

    c.execute('''CREATE TABLE schema_map
                                     (sc_schema_name text, native_db text, native_db_platform text)''')

    c.execute("INSERT INTO lookup_meta VALUES ('ImageOwners','OwnerID','int')")

    c.execute("INSERT INTO lookup VALUES ('1', 'user1')")
    c.execute("INSERT INTO lookup VALUES ('2', 'user2')")
    c.execute("INSERT INTO lookup VALUES ('3', 'user3')")

    for i in app_conf['db_schemas']:
        c.execute(f"INSERT INTO schema_map VALUES ('{i['schema_name']}', '{i['database']}', '{i['db_platform']}')")

    conn.commit()
    conn.close()

    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    log.info('Test user2 == 2')
    t = ('user2',)
    c.execute('SELECT native_id FROM lookup WHERE eos_account=?', t)
    res = c.fetchone()[0]
    print("user2 native ID:", res)

    conn.close()


def process():
    create_app1()
    create_app2()
    create_app3()
    # TODO: have Docker composer copy respective lookup DBs to haiku_node/lookup/unification_lookup.db


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
    process()
