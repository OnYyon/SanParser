import os
import sqlite3 as sql


class Db:
    def __init__(self):
        try:
            os.makedirs("./_out/temp")
        except FileExistsError:
            os.remove("./_out/temp/data.db")
        self.con = sql.connect("./_out/temp/data.db")
        self.cur = self.con.cursor()

    def create_tabel(self, table_name: str, *columns):
        pattern = '"' + '", "'.join(map(lambda x: " ".join(x), columns)) + '"'
        self.cur.execute(f'CREATE TABLE IF NOT EXISTS "{table_name}"'
                         f'({pattern});')
        self.con.commit()

    def insert_into_table(self, table_name: str, *args):
        pattern = '", "'.join(args)
        self.cur.execute(f'INSERT INTO "{table_name}" VALUES ("{pattern}");')
        self.con.commit()

    def kill_session(self):
        self.con.close()
