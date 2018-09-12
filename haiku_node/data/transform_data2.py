import os
import json

import base64
import logging
import time

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sqlite3


class TransformDataJSON:

    def __init__(self, data_source_parms):
        self.__data_source_parms = data_source_parms

    def get_rows_as_dicts(self, cursor):
        cursor.execute(assemble_query_string())
        columns = [d[0] for d in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_tables(self, cursor):
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return [r[0] for r in cursor.fetchall()]

    def to_json(self, conn):
        """

        :param conn: An open SQLite connection
        :return: A JSON representation of the contents
        """

        curr = conn.cursor()
        dump = {}

        for t in self.get_tables(curr):
            curr.execute("SELECT * FROM `{}`".format(t))
            dump[t] = self.get_rows_as_dicts(curr, t)

        #Building header
        dump['header'].append({'from': self.__data_source_parms['providing_app'],
                               'timestamp': int(time.time())})

        unification_users = self.__data_source_parms['unification_ids']

        for unification_id_key in unification_users:
            dump['unification users'].append({'unification user': unification_users[unification_id_key]})

        return json.dumps(dump)

    def fetch_json_data(self):
        # connString = '{obdc}:///{filename}' \
        #     .format(
        #     odbc=self.__data_source_parms['odbc'],
        #     filename=self.__data_source_parms['filename'], )

        conn = sqlite3.connect(self.__data_source_parms['filename'])
        j = self.to_json(conn)
        conn.close()

        return j
