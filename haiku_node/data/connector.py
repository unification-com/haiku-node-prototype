from sqlalchemy import create_engine

from haiku_node.config.config import UnificationConfig
from haiku_node.data.transform_data import fetch_user_data


def assemble_connection_string(data_source):
    odbc = data_source['odbc']
    user = data_source['user']
    passw = data_source['pass']
    host = data_source['host']
    database = data_source['database']

    # TODO: The data source should have the port
    port = '3306'
    return f'{odbc}://{user}:{passw}@{host}:{port}/{database}'


def app_connector(data_source_params):
    conn_string = assemble_connection_string(data_source_params)
    return create_engine(conn_string)


def run_query(engine, query):
    t = engine.execute(query)
    result = [r[0] for r in t]
    return str(result)


def evaluate(data_source_params):
    engine = app_connector(data_source_params)

    if data_source_params['database'] == 'Heartbit':
        return run_query(engine, "SELECT FirstName FROM Users;")

    if data_source_params['database'] == 'Datablobs':
        return run_query(engine, "SELECT Name FROM BlobCreator;")


if __name__ == "__main__":
    """
    Testing fetch_user_data
    """
    config = UnificationConfig()
    app_config = config.demo_app_config()
    engine = app_connector(app_config)

    res = fetch_user_data(app_config['data_source_params'])
    print(res)
