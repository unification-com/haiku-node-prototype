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
    # target = target_file(db_name)

    # transformer = TransformDataJSON(str(target), {'1': 'user1'})
    # j = transformer.transform()

    # print(j)


def test_data_factory():
    data_source_parms = {
        'filename': str(target_file("app1.db")),
        'userTable': 'Users',
        'dataTable': 'UserData',
        'userIdentifier': 'ID',
        'dataUserIdentifier': 'UserID',
        'dataColumnsToInclude': ['Heartrate', 'Pulse'],
        'native_user_ids': ['1', '2'],
        'base64_encode_cols': [],
        'providing_app': 'app1',
        'unification_id_map': {'1': 'user1', '2': 'user2'},
        'db_schema': {'tmp': 'tmp'}
    }

    transformer = TransformDataJSON(data_source_parms)
    j = transformer.transform()
    print(j)


if __name__ == "__main__":
    test_data_factory()
