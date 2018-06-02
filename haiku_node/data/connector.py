from sqlalchemy import create_engine

heartbit_data_source_parms = {
    'odbc': 'mysql+mysqlconnector',
    'database': 'Heartbit',
    'host': 'db',
    'user': 'heartbit_user',
    'pass': 'password',
    'userTable': 'Users',
    'dataTable': 'UserData',
    'userIdentifier': 'ID',
    'dataUserIdentifier': 'UserID',
    'dataColumnsToInclude': ['Heartrate', 'GeoLocation', 'TimeStamp', 'Pulse']
}

blobdata_data_source_parms = {
    'odbc': 'mysql+mysqlconnector',
    'database': 'Datablobs',
    'host': 'db',
    'user': 'datablobs_user',
    'pass': 'password',
    'userTable': 'BlobCreator',
    'dataTable': 'BlobData',
    'userIdentifier': 'CreatorID',
    'dataUserIdentifier': 'CreatorID',
    'dataColumnsToInclude': ['DataBlob', 'BlobSize']
}


def assemble_connection_string(data_source):
    odbc = data_source['odbc']
    user = data_source['user']
    passw = data_source['pass']
    host = data_source['host']
    database = data_source['database']

    # TODO: The datasource should have the port
    port = '3306'
    return f'{odbc}://{user}:{passw}@{host}:{port}/{database}'


def excercise_connection(source, query):
    conn_string = assemble_connection_string(source)
    engine = create_engine(conn_string)
    t = engine.execute(query)
    result = [r[0] for r in t]
    print(result)


def process():
    excercise_connection(
        heartbit_data_source_parms, "SELECT FirstName FROM Users;")
    excercise_connection(
        blobdata_data_source_parms, "SELECT Name FROM BlobCreator;")


if __name__ == "__main__":
    process()
