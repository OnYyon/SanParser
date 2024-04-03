import os
import fnmatch

from db import Db


class San:
    def __init__(self, path_to_file):
        self.path_to_file = path_to_file
        self.lines = {}
        self.db = Db()

    def find_info(self, path_to_file) -> dict:
        try:
            file_name = fnmatch.filter(os.listdir(f"./_in/{path_to_file}/"), "*SSHOW_SYS*.txt")[0]
        except IndexError:
            print("Программа не нашла нужный файл")
        else:
            f = open(f"./_in/{path_to_file}/{file_name}")
        flag = False
        self.lines = {}
        while True:
            line = f.readline()
            if "switchName:" in line:
                flag = True
            if flag:
                self.lines[line.split(":")[0].strip()] = "".join(line.split(":", maxsplit=1)[1::]).strip()
            if "zoning" in line:
                flag = False
            if "Fabric Name:" in line:
                self.lines[line.split(":")[0].strip()] = "".join(line.split(":", maxsplit=1)[1::]).strip()
            if not line:
                break
        try:
            self.lines["Fabric Name"]
        except KeyError:
            self.lines["Fabric Name"] = "No"
        self.lines["zoning"] = self.lines["zoning"].strip("ON ()")
        swt_name = self.lines["switchName"]
        fb_name = self.lines["Fabric Name"]
        self.db.create_tabel(f"data_{fb_name}_{swt_name}", self.lines.keys())
        self.db.insert_into_table(f"data_{fb_name}_{swt_name}", self.lines.values())
        return self.lines
