import os
from pathlib import Path

import sqlite3
from sqlite3 import Error

import pytest

import json


def target_file(db_name):
    current_directory = Path(os.path.dirname(os.path.abspath(__file__)))
    p = current_directory / 'data/sqlite'
    return p / db_name


def get_tables(cursor):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return [r[0] for r in cursor.fetchall()]


def to_json(conn):
    curr = conn.cursor()
    dump = {}
    for t in get_tables(curr):
        curr.execute("SELECT * FROM `{}`".format(t))
        dump[t] = get_rows_as_dicts(curr, t)
    return json.dumps(dump)


def get_rows_as_dicts(cursor, table):
    cursor.execute("SELECT * FROM `{}`".format(table))
    columns = [d[0] for d in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


@pytest.mark.parametrize(
    "db_name", ["datablob.db", "heartbit.db", "imagestorage.db"])
def test_database_read(db_name):
    """ create a database connection to the SQLite database
        specified by the db_name

    :param db_name: database file
    :return: Connection object or None
    """
    target = target_file(db_name)
    try:
        conn = sqlite3.connect(str(target))
        j = to_json(conn)
        print(j)

    except Error as e:
        print(e)
