import os
from pathlib import Path

import sqlite3

import pytest


def target_file(db_name):
    current_directory = Path(os.path.dirname(os.path.abspath(__file__)))
    p = current_directory / 'data/sqlite'
    return p / db_name


@pytest.mark.parametrize(
    "db_name", ["datablob.db", "heartbit.db", "imagestorage.db"])
def test_database_read(db_name):
    target = target_file(db_name)
    conn = sqlite3.connect(str(target))
    curr = conn.cursor()
