import os
from zipfile import ZipFile


def prepare():
    if len(os.listdir()) != 0:
        lst = os.listdir("./uploads")
        for i in lst:
            with ZipFile(f"./uploads/{i}") as zf:
                zf.extractall("./uploads")
            os.remove(f"./uploads/{i}")
