import os
from xlsxwriter import Workbook

from core.main import SanParser
from core.decom import switch_or_director
from core.writer import Writer
from core.db import Db


def parsing():
    db = Db()
    san = SanParser()
    writer = Writer()
    lst = os.listdir("./uploads")
    lst = list(filter(lambda x: not x.startswith("."), lst))
    if "__MACOSX" in lst:
        lst.remove("__MACOSX")
    for i in lst:
        try:
            switch_or_director(i)
        except NotADirectoryError:
            continue
        data = san.find_info(i)
        san.find_alias(i)
        san.find_zone(i)
        san.find_switch(i)
        san.find_nsshowr(i)
        tables = san.find_nscamshow(i)
        san.find_fabric(i)
        san.find_errshow(i)
        swt_name = data["switchName"]
        fb_name = data["Fabric Name"]
        if "_out" not in os.listdir():
            os.mkdir("_out")
        with open(f"./_out/Analysis_{fb_name}_{swt_name}.xlsx", "w") as f:
            workbook = Workbook(f'./_out/Analysis_{fb_name}_{swt_name}.xlsx')
        writer.write_fabric(fb_name, swt_name, workbook)
        writer.write_switches(fb_name, swt_name, workbook)
        writer.wrtie_zone(fb_name, swt_name, workbook)
        workbook.close()


if __name__ == "__main__":
    parsing()
