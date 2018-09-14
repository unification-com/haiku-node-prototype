import os
import pytest

from pathlib import Path

from haiku_node.data.transform_data2 import TransformDataJSON

data_source_parms = {'app1': {
        'userTable': 'Users',
        'dataTable': 'UserData',
        'userIdentifier': 'ID',
        'dataUserIdentifier': 'UserID',
        'dataColumnsToInclude': ['Heartrate', 'Pulse'],
        'native_user_ids': ['1', '2'],
        'base64_encode_cols': [],
        'providing_app': 'app1',
        'unification_id_map': {'1': 'user1', '2': 'user2'},
        'db_schema': {}
    },
    'app2': {
        'userTable': 'BlobCreator',
        'dataTable': 'BlobData',
        'userIdentifier': 'CID',
        'dataUserIdentifier': 'CreatorID',
        'dataColumnsToInclude': ['DataBlob', 'BlobSize'],
        'native_user_ids': ['1', '2'],
        'base64_encode_cols': [],
        'providing_app': 'app2',
        'unification_id_map': {'1': 'user1', '2': 'user2'},
        'db_schema': {}
    },
    'app3': {
        'userTable': 'ImageOwners',
        'dataTable': 'ImageData',
        'userIdentifier': 'OID',
        'dataUserIdentifier': 'OwnerID',
        'dataColumnsToInclude': ['Image'],
        'native_user_ids': ['1', '2'],
        'base64_encode_cols': [],
        'providing_app': 'app3',
        'unification_id_map': {'1': 'user1', '2': 'user2'},
        'db_schema': {}
    }
}


def target_file(db_name):
    current_directory = Path(os.path.dirname(os.path.abspath(__file__)))
    p = current_directory / 'data/sqlite'
    return p / db_name


@pytest.mark.parametrize(
    "app_name", ["app1", "app2", "app3"])
def test_database_read(app_name):
    """ create a database connection to the SQLite database
        specified by the app_name

    :param app_name: app name
    :return: Connection object or None
    """
    target = str(target_file(f'{app_name}.db'))

    d_params = data_source_parms[app_name]
    d_params['filename'] = target

    transformer = TransformDataJSON(d_params)
    j = transformer.transform()

    print(j)
