import os
import sqlite3 as sql


class Db:
    def __init__(self):
        self.con = sql.connect("./db/data.db")
        self.cur = self.con.cursor()

    def create_tabel(self, table_name, columns):
        self.cur.execute(f'CREATE TABLE IF NOT EXISTS "{table_name}" ({columns});')
        self.con.commit()

    def insert_into_table(self, table_name, *args):
        try:
            args = tuple(map(lambda x: x.replace('"', ''), args))
            pattern = "', '".join(args)
            if "(" in table_name:
                table_name, columns = table_name.split("(", maxsplit=1)
                self.cur.execute(f"INSERT INTO {table_name}({columns} VALUES ('{pattern}');")
            else:
                self.cur.execute(f"INSERT INTO '{table_name}' VALUES ('{pattern}');")
            self.con.commit()
        except Exception as e:
            # print(e)
            return False
        return True

    def update_table(self, table_name, column_what, what, column_where, where):
        table_name = table_name.replace('"', "")
        column_what = column_what.replace('"', "")
        what = what.replace('"', "")
        column_where = column_where.replace('"', "")
        where = where.replace('"', "")
        self.cur.execute(f'UPDATE "{table_name}" SET "{column_what}" = "{what}" WHERE "{column_where}" = "{where}"')
        self.con.commit()

    def select(self, table_name, what, need_where=False, where=""):
        if not need_where:
            lst = self.cur.execute(f'SELECT {what} FROM "{table_name}"').fetchall()
        else:
            lst = self.cur.execute(f'SELECT {what} FROM "{table_name}" WHERE {where}').fetchall()
        return lst

    def kill_session(self):
        self.con.close()
