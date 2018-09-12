import json
import sqlite3


class TransformDataJSON:

    def __init__(self, sqlite_file, unification_ids):
        self.unification_ids = unification_ids
        self.sqlite_file = sqlite_file

    def get_rows_as_dicts(self, cursor, table):
        cursor.execute("SELECT * FROM `{}`".format(table))
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

        #TODO: Get these unification users from somewhere
        unification_users = []
        for unification_id_key in unification_users:
            dump['unification users'].append(
                {'unification user': unification_users[unification_id_key]})

        return json.dumps(dump)

    def fetch_json_data(self):
        conn = sqlite3.connect(self.sqlite_file)
        j = self.to_json(conn)
        conn.close()

        return j
