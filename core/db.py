import os
import sqlite3 as sql


class Db:
    def __init__(self):
        try:
            os.makedirs("../_out/temp")
        except FileExistsError:
            os.remove("../_out/temp/data.db")
        self.con = sql.connect("../_out/temp/data.db")
        self.cur = self.con.cursor()

    def create_tabel(self, table_name: str, *columns):
        try:
            pattern = '"' + '", "'.join(map(lambda x: " ".join(x), columns)) + '"'
            self.cur.execute(f'CREATE TABLE IF NOT EXISTS "{table_name}"'
                             f'({pattern});')
            self.con.commit()
        except Exception:
            return False
        return True

    def insert_into_table(self, table_name: str, *args):
        try:
            pattern = '", "'.join(args)
            self.cur.execute(f'INSERT INTO "{table_name}" VALUES ("{pattern}");')
            self.con.commit()
        except Exception:
            return False
        return True

    def update_table(self, table_name, column_what, what, column_where, where):
        try:
            self.cur.execute(f'UPDATE {table_name} SET "{column_what}" = "{what}"'
                             f'WHERE "{column_where}" = "{where}"')
            self.con.commit()
        except Exception:
            return False
        return True

    def kill_session(self):
        self.con.close()
