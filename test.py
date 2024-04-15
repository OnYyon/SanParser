#! -*- coding: utf-8 -*-
# !/usr/local/bin/python3.8

import os
from datetime import datetime
from xlsxwriter import Workbook

from core.main import SanParser
from core.decom import switch_or_director
from core.writer import Writer
from core.db import Db

db = Db()
san = SanParser()
writer = Writer()

try:
    os.mkdir("../_in")
except FileExistsError:
    print(
        "Директория \"_in\" уже существует\nЛибо удалите или переименуйте директорию, либо перемистите файл *.py\nИ перезапустить файл")
else:
    print("Сложите фалы в директорию _in")
    var = input("Как будет все готово нажмите ENTER:")
    if var == "":
        lst = os.listdir("./_in")
        tables = db.select("sqlite_master", "name", True, "type=\"table\"")
        st = datetime.now()
        for i in lst:
            try:
                switch_or_director(i)
            except Exception:
                pass
            try:
                data = san.find_info(i)
                san.find_alias(i)
                san.find_zone(i)
                san.find_switch(i)
                san.find_nsshowr(i)
                tables = san.find_nscamshow(i)
                san.find_fabric(i)
            except Exception:
                pass
            try:
                swt_name = data["switchName"]
                fb_name = data["Fabric Name"]
                os.mkdir(f"./_out/{fb_name}_{swt_name}")
                temp_f = open(f"./_out/{fb_name}_{swt_name}/Analysis_{fb_name}_{swt_name}.xlsx", "w+")
                workbook = Workbook(f'./_out/{fb_name}_{swt_name}/Analysis_{fb_name}_{swt_name}.xlsx')
                writer.write_fabric(fb_name, swt_name, workbook)
                writer.write_switches(fb_name, swt_name, tables, workbook)
                writer.wrtie_zone(fb_name, swt_name, workbook)
                workbook.close()
            except Exception:
                pass

end = datetime.now()
print(f"\n================================\nTime: {end - st}\n================================")
