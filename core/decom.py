import os
import gzip
import fnmatch


def switch_or_director(path_to_file: str):
    try:
        lst = ["*S0*SSHOW_SYS*.txt.gz", "*S0*SSHOW_SEC*.txt.gz", "*S0*SSHOW_FABRIC*.txt.gz",
               "*S0*SSHOW_SERVICE*.txt.gz"]
        for i in lst:
            files = fnmatch.filter(os.listdir(f"./uploads/{path_to_file}"), i)[0]
            with gzip.GzipFile(f"./uploads/{path_to_file}/{files}", "rb") as dec_file:
                string = dec_file.read()
                with open(f"uploads/{path_to_file}/{files.replace('.gz', '')}", "wb") as f:
                    f.write(string)
    except IndexError:
        files = fnmatch.filter(os.listdir(f"./uploads/{path_to_file}"), "*SSHOW_SYS*.txt.gz")[0]
        with gzip.GzipFile(f"./uploads/{path_to_file}/{files}", "r") as dec_file:
            flag = False
            while True:
                line = dec_file.readline()
                if b"firmwareshow -v" in line:
                    flag = True
                    continue
                if b"real" in line and flag:
                    break
                if flag:
                    if b"Slot Name" in line:
                        continue
                    else:
                        if b"ACTIVE" in line:
                            slot = line.split()[0]
        slot = slot.decode()
        lst = [f"*S{slot}*SSHOW_SYS*.txt.gz", f"*S{slot}*SSHOW_SEC*.txt.gz", f"*S{slot}*SSHOW_FABRIC*.txt.gz",
               f"*S{slot}*SSHOW_SERVICE*.txt.gz"]
        for i in lst:
            files = fnmatch.filter(os.listdir(f"./uploads/{path_to_file}"), i)[0]
            with gzip.GzipFile(f"./uploads/{path_to_file}/{files}", "rb") as dec_file:
                string = dec_file.read()
                with open(f"uploads/{path_to_file}/{files.replace('.gz', '')}", "wb") as f:
                    f.write(string)
