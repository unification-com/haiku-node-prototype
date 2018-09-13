import json
import sqlite3


class TransformDataJSON:

    def __init__(self, data_source_parms):
        self.sqlite_file = data_source_parms['filename']
        self.__data_source_parms = data_source_parms

    def transform(self):
        conn = sqlite3.connect(self.sqlite_file)
        j = self.__to_json(conn)
        conn.close()

        return j

    def __to_json(self, conn):
        """

        :param conn: An open SQLite connection
        :return: A JSON representation of the contents
        """
        curr = conn.cursor()
        dump = self.__get_rows_as_dicts(curr)

        unif_ids = []
        for key, val in list(self.__data_source_parms['unification_id_map'].items()):
            unif_ids.append(val)

        ret = {'data': self.__prepare(dump),
               'unification_users': unif_ids}

        return json.dumps(ret)

    def __get_rows_as_dicts(self, cursor):
        cursor.execute(self.__get_query_string())
        columns = [d[0] for d in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def __prepare(self, dump):
        prepared_dump = []
        for d in dump:
            # change Native IDs to Unification IDs
            nid = str(d[self.__data_source_parms['userIdentifier']])
            d[self.__data_source_parms['userIdentifier']] = self.__data_source_parms['unification_id_map'][nid]
            d['account_name'] = d.pop(self.__data_source_parms['userIdentifier'])

            # Todo - encode images into base64
            prepared_dump.append(d)

        return prepared_dump

    def __get_query_string(self):
        data_columns = ""
        native_user_ids_str = ','.join(self.__data_source_parms['native_user_ids'])

        for item in self.__data_source_parms['dataColumnsToInclude']:
            data_columns += '{dataTable}.{item},'\
                .format(dataTable=self.__data_source_parms['dataTable'],
                        item=item)

        data_columns = data_columns.rstrip(",")

        query_string = 'SELECT {userTable}.{userIdentifier}, {dataColumns} ' \
                       'FROM {userTable} LEFT JOIN {dataTable} ' \
                       'On {userTable}.{userIdentifier} = {dataTable}.{dataUserIdentifier} ' \
                       'WHERE {userTable}.{userIdentifier} IN ({native_user_ids}) ' \
                       'ORDER BY {userTable}.{userIdentifier}' \
            .format(
                dataColumns=data_columns,
                dataTable=self.__data_source_parms['dataTable'],
                userTable=self.__data_source_parms['userTable'],
                userIdentifier=self.__data_source_parms['userIdentifier'],
                dataUserIdentifier=self.__data_source_parms['dataUserIdentifier'],
                native_user_ids=native_user_ids_str)

        return query_string
