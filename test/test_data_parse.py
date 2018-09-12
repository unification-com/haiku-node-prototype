import os
import pytest

from pathlib import Path

from haiku_node.data.transform_data2 import TransformDataJSON


def target_file(db_name):
    current_directory = Path(os.path.dirname(os.path.abspath(__file__)))
    p = current_directory / 'data/sqlite'
    return p / db_name


@pytest.mark.parametrize(
    "db_name", ["app1.db", "app2.db", "app3.db"])
def test_database_read(db_name):
    """ create a database connection to the SQLite database
        specified by the db_name

    :param db_name: database file
    :return: Connection object or None
    """
    target = target_file(db_name)

    transformer = TransformDataJSON(str(target), {'1': 'user1'})
    j = transformer.fetch_json_data()

    print(j)
