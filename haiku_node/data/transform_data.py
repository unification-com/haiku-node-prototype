import bonobo
import bonobo_sqlalchemy
import logging
from sqlalchemy import create_engine
from bonobo.config.processors import ContextProcessor, use_context

class TransformData:

    def __init__(self, data_source_parms):
        self.__data_source_parms = data_source_parms

    def write_to_string(self, *args, **kwargs):
        self.__result_string += args[0]

    def build_xml_document_header(self):
        self.__result_string = '<data>\n\t<from>{vfrom}</from>\n\t<timestamp>{time}\
            </timestamp>\n\t<unification_users>\n'.format(vfrom='TODO', time=89374893798)
        
        unification_users = self.__data_source_parms['unification_ids']

        for unification_id_key in unification_users:
            self.__result_string += '\t\t<unification_user>'
            self.__result_string += unification_users[unification_id_key]
            self.__result_string += '</unification_user>\n'

        self.__result_string += '\t</unification_users>\n\t<rows>\n'

    def build_xml_document_footer(self):
        self.__result_string += '\t</rows>\n</data>\n'

    #@bonobo.config.use_context_processor(xml_document)
    @use_context
    def create_xml(self, context, *args, **kwargs):
        iter = 0;
        yield '\t\t<row>\n'
        fields = context.get_input_fields()
        for item in args:
            field_string = fields[iter]

            if fields[iter] == self.__data_source_parms['userIdentifier']:
                newItem = self.__data_source_parms['unification_ids'][str(item)]
                item = newItem
                field_string = 'account_name'

            yield '\t\t\t<field>\n\t\t\t\t<field_name>{id}</field_name>\n\t\t\t\t<value>{value}</value>\n\t\t\t\t<type>{type}</type>\n\t\t\t</field>\n'.format(id=field_string, value=item, type=type(item).__name__)

            iter += 1

        yield '\t\t</row>\n'

    def get_graph(self):
        graph = bonobo.Graph()
        graph.add_chain(
            #   NOTE: The Select statement here assumes a default engine of sqlalchemy.engine
            #   defined in get_services()
            #   I'm fairly sure this can be overridden with paremeters
            bonobo_sqlalchemy.Select(self.assemble_query_string(), limit=100),
            self.create_xml,
            self.write_to_string
        )
        return graph


    def get_services(self, connString):
        #   NOTE: This set is the set of all available services
        #   right now we only have sqlalchemy engine, with a connstring hardcoded to
        #   a mysqldb ODBC database, but obviously that is parameterizalable
        return {
            'sqlalchemy.engine':create_engine(connString)
        }


    def assemble_connection_string(self):
        connString = '{odbc}://{user}:{passw}@{host}/{database}' \
            .format(
                odbc=self.__data_source_parms['odbc'],
                user=self.__data_source_parms['user'],
                passw=self.__data_source_parms['pass'],
                host=self.__data_source_parms['host'],
                database=self.__data_source_parms['database'])

        return connString

    def assemble_query_string(self):
        dataColumns = ""
        length = len(self.__data_source_parms['dataColumnsToInclude'])
        iter = 1
        comma = ''

        native_user_ids_str = ','.join(self.__data_source_parms['native_user_ids'])

        for item in self.__data_source_parms['dataColumnsToInclude']:
            if iter != length:
                comma = ','
            else:
                comma = ''

            dataColumns += '{dataTable}.{item}{comma}'.format(dataTable=self.__data_source_parms['dataTable'], item=item,comma=comma)
            iter = iter + 1

        queryString = 'SELECT {userTable}.{userIdentifier}, {dataColumns} FROM {userTable} LEFT JOIN {dataTable} ' \
                  'On {userTable}.{userIdentifier} = {dataTable}.{dataUserIdentifier} ' \
                  'WHERE {userTable}.{userIdentifier} IN ({native_user_ids}) ' \
                  'ORDER BY {userTable}.{userIdentifier}' \
                .format(
                    dataColumns = dataColumns,
                    dataTable=self.__data_source_parms['dataTable'],
                    userTable=self.__data_source_parms['userTable'],
                    userIdentifier=self.__data_source_parms['userIdentifier'],
                    dataUserIdentifier=self.__data_source_parms['dataUserIdentifier'],
                    native_user_ids=native_user_ids_str)

        return queryString

    def fetch_user_data(self):
        try:
            self.build_xml_document_header()
            connString = self.assemble_connection_string()
            bonobo.run(self.get_graph(),services=self.get_services(connString))
            self.build_xml_document_footer()

        except Exception as e:
            logging.warning("Exception caught: fetch_user_data")
            logging.warning(e)
            logging.warning(self.__data_source_parms)
            return 'FAIL DATA'

        return self.__result_string
