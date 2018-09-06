import os
from pathlib import Path

import sqlite3
from sqlite3 import Error

import pytest

import csv


def target_file(db_name):
    current_directory = Path(os.path.dirname(os.path.abspath(__file__)))
    p = current_directory / 'data/sqlite'
    return p / db_name

@pytest.mark.parametrize(
    "db_name", ["datablob.db", "heartbit.db", "imagestorage.db"])
def test_database_read(db_name):
    """ create a database connection to the SQLite database
        specified by the db_name

    :param db_file: database file
    :return: Connection object or None
    """
    target = target_file(db_name)
    try:
        conn = sqlite3.connect(str(target))
        return conn
    except Error as e:
        print(e)



# def show_tables(conn):
#     """
#     Query all rows in the tasks table
#     :param conn: the Connection object
#     :return:
#     """
#     try:
#         curr = conn.cursor()
#         curr.execute("SELECT name FROM sqlite_master WHERE type='table';")
#         tables = curr.fetchall()
#         for tbl in tables:
#             print("\n########  " + tbl[0] + "  ########")
#             curr.execute("SELECT * FROM " + tbl[0] + ";")
#             print(*[i[0] for i in curr.description])
#             rows = curr.fetchall()
#             for row in rows:
#                 print(row)
#     except KeyboardInterrupt:
#         print("\nClean Exit By user")
#     finally:
#         print("\nFinally")




connection = test_database_read('imagestorage.db')
#tables = show_tables(connection)

def to_csv(conn):
    curr = conn.cursor()
    curr.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = curr.fetchall()
    for t in tables:
        curr.execute("SELECT * FROM `{}`".format(t[0]))
        tempcsv = 'data/sqlite/{}_data.csv'.format(t[0])
        with open(tempcsv, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([i[0] for i in curr.description])   # COLUMN HEADERS
            for row in curr.fetchall():
                writer.writerow(row)
        csvfile.close()
to_csv(connection)
