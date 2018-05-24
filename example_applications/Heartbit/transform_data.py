import bonobo
import requests
from sqlalchemy import create_engine
import bonobo_sqlalchemy
    	
def get_graph(**options):
    graph = bonobo.Graph()
    graph.add_chain(
        #   NOTE: The Select statement here assumes a default engine of sqlalchemy.engine
        #   defined in get_services()
        #   I'm fairly sure this can be overridden with paremeters
        bonobo_sqlalchemy.Select('SELECT * FROM UserData LEFT JOIN Users On Users.ID = UserData.UserID', limit=100),
        bonobo.PrettyPrinter(),
    )
    return graph
  
def get_services(**options):
    connString = 'mysql+mysqldb://Heartbit:Heartbit@localhost/Heartbit'
    
    #   NOTE: This set is the set of all available services
    #   right now we only have sqlalchemy engine, with a connstring hardcoded to
    #   a mysqldb ODBC database, but obviously that is parameterizalable
    return {    
        'sqlalchemy.engine':create_engine(connString)
    }

# The __main__ block actually execute the graph.
if __name__ == '__main__':
    parser = bonobo.get_argument_parser()
    with bonobo.parse_args(parser) as options:
        bonobo.run(get_graph(**options),services=get_services(**options))