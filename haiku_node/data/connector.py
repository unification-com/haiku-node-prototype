from sqlalchemy import create_engine

from haiku_node.config.config import UnificationConfig


def assemble_connection_string(data_source):
    odbc = data_source['odbc']
    user = data_source['user']
    passw = data_source['pass']
    host = data_source['host']
    database = data_source['database']

    # TODO: The data source should have the port
    port = '3306'
    return f'{odbc}://{user}:{passw}@{host}:{port}/{database}'


def app_connector(app_config):
    params = app_config['data_source_params']
    conn_string = assemble_connection_string(params)
    engine = create_engine(conn_string)
    return engine


def run_query(engine, query):
    t = engine.execute(query)
    result = [r[0] for r in t]
    print(result)


def evaluate():
    config = UnificationConfig()
    app_config = config.demo_app_config()
    engine = app_connector(app_config)

    if app_config['data_source_params']['database'] == 'Heartbit':
        run_query(engine, "SELECT FirstName FROM Users;")

    if app_config['data_source_params']['database'] == 'Datablobs':
        run_query(engine, "SELECT Name FROM BlobCreator;")


if __name__ == "__main__":
    evaluate()
