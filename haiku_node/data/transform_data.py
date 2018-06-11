import bonobo
import bonobo_sqlalchemy

from sqlalchemy import create_engine
from bonobo.config.processors import ContextProcessor, use_context
from haiku_node.lookup.eos_lookup import UnificationLookup
import logging

returnString = ""
global_parms = []

def write_to_string(*args, **kwargs):
    global returnString
    returnString += args[0]

def xml_document(self, context):
    leadString = '<data>\n\t<from>{vfrom}</from>\n\t<timestamp>{time}</timestamp>\n\t<unification_users>\n'
    unification_users = global_parms['unification_ids']

    for unification_id_key in unification_users:
        leadString += '\t\t<unification_user>'
        leadString += unification_users[unification_id_key]
        leadString += '</unification_user>\n'

    leadString += '\t</unification_users>\n\t<rows>\n'.format(vfrom='TODO', time=89374893798)
    context.send(leadString)
    yield
    context.send('\t</rows>\n</data>\n')


@use_context
@bonobo.config.use_context_processor(xml_document)
def create_xml(context, *args, **kwargs):
    iter = 0;
    global global_parms

    yield '\t\t<row>\n'
    fields = context.get_input_fields()
    for item in args:
        field_string = fields[iter]

        if fields[iter] == global_parms['userIdentifier']:
            newItem = global_parms['unification_ids'][str(item)]
            item = newItem
            field_string = 'unification_id'

        yield '\t\t\t<field>\n\t\t\t\t<field_name>{id}</field_name>\n\t\t\t\t<value>{value}</value>\n\t\t\t\t<type>{type}</type>\n\t\t\t</field>\n'.format(id=field_string, value=item, type=type(item))

        iter += 1

    yield '\t\t</row>\n'

def get_graph(data_source_parms):

    graph = bonobo.Graph()
    graph.add_chain(
        #   NOTE: The Select statement here assumes a default engine of sqlalchemy.engine
        #   defined in get_services()
        #   I'm fairly sure this can be overridden with paremeters
        bonobo_sqlalchemy.Select(assemble_query_string(data_source_parms), limit=100),
        create_xml,
        write_to_string
    )
    return graph


def get_services(connString):
    #   NOTE: This set is the set of all available services
    #   right now we only have sqlalchemy engine, with a connstring hardcoded to
    #   a mysqldb ODBC database, but obviously that is parameterizalable
    return {    
        'sqlalchemy.engine':create_engine(connString)
    }


def assemble_connection_string(data_source_parms):
    connString = '{odbc}://{user}:{passw}@{host}/{database}' \
        .format(
            odbc=data_source_parms['odbc'],
            user=data_source_parms['user'],
            passw=data_source_parms['pass'],
            host=data_source_parms['host'],
            database=data_source_parms['database'])
    
    return connString


def assemble_query_string(data_source_parms):
    dataColumns = ""
    length = len(data_source_parms['dataColumnsToInclude'])
    iter = 1
    comma = ''

    native_user_ids_str = ','.join(data_source_parms['native_user_ids'])
    
    for item in data_source_parms['dataColumnsToInclude']:
        if iter != length:
            comma = ','
        else:
            comma = ''
            
        dataColumns += '{dataTable}.{item}{comma}'.format(dataTable=data_source_parms['dataTable'], item=item,comma=comma)
        iter = iter + 1

    queryString = 'SELECT {userTable}.{userIdentifier}, {dataColumns} FROM {userTable} LEFT JOIN {dataTable} ' \
                  'On {userTable}.{userIdentifier} = {dataTable}.{dataUserIdentifier} ' \
                  'WHERE {userTable}.{userIdentifier} IN ({native_user_ids}) ' \
                  'ORDER BY {userTable}.{userIdentifier}' \
            .format(
                dataColumns = dataColumns,
                dataTable=data_source_parms['dataTable'],
                userTable=data_source_parms['userTable'],
                userIdentifier=data_source_parms['userIdentifier'],
                dataUserIdentifier=data_source_parms['dataUserIdentifier'],
                native_user_ids=native_user_ids_str)
    
    return queryString


def fetch_user_data(data_source_parms):
    global global_parms
    global_parms = data_source_parms

    try:
        connString = assemble_connection_string(data_source_parms)
        bonobo.run(get_graph(data_source_parms),services=get_services(connString))
        
    except Exception as e:
        logging.warning("Exception caught: fetch_user_data")
        logging.warning(e)
        logging.warning(data_source_parms)
        return 'FAIL DATA'
   
    return returnString
