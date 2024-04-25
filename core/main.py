import os
import fnmatch

from core.db import Db


class SanParser:
    def __init__(self):
        self.lines = {}
        self.db = Db()
        self.db.create_tabel("data_of_switchs", "SwitchName Text, FabricName Text, wwn Text")

    def find_info(self, path_to_file) -> dict:
        try:
            file_name = fnmatch.filter(os.listdir(f"./uploads/{path_to_file}/"), "*SSHOW_SYS*.txt")[0]
        except IndexError:
            print("Программа не нашла нужный файл")
        else:
            f = open(f"./uploads/{path_to_file}/{file_name}")
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
        self.db.create_tabel(f"data_{fb_name}_{swt_name}", " Text, ".join(self.lines.keys()) + " Text")
        self.db.insert_into_table(f"data_{fb_name}_{swt_name}", *self.lines.values())
        self.db.insert_into_table("data_of_switchs", swt_name, fb_name, self.lines["switchWwn"])
        return self.lines

    def find_zone(self, path_to_file):
        try:
            file_name = fnmatch.filter(os.listdir(f"./uploads/{path_to_file}/"), "*SSHOW_SYS*.txt")[0]
        except IndexError:
            print("Программа не нашла нужный файл")
        else:
            f = open(f"./uploads/{path_to_file}/{file_name}")
        zones = {}
        while True:
            line = f.readline()
            if not line:
                break
            if "zone." in line:
                flag = True
            else:
                continue
            if flag:
                name = line.split(":", maxsplit=1)[0].replace("zone.", "")
                zone_memmber = line.split(":", maxsplit=1)[1].strip()
                zones[name] = zone_memmber
        swt_name = self.lines["switchName"]
        fb_name = self.lines["Fabric Name"]
        self.db.create_tabel(f"zone_cfg_{fb_name}_{swt_name}", "zone TEXT, zone_members TEXT")
        for key, val in zones.items():
            self.db.insert_into_table(f"zone_cfg_{fb_name}_{swt_name}", key, val)
        self.db.con.commit()

    def find_alias(self, path_to_file):
        try:
            file_name = fnmatch.filter(os.listdir(f"./uploads/{path_to_file}/"), "*SSHOW_SYS*.txt")[0]
        except IndexError:
            print("Программа не нашла нужный файл")
        else:
            f = open(f"./uploads/{path_to_file}/{file_name}")
        aliases = {}
        flag = False
        while True:
            line = f.readline()
            if "defzone:" in line:
                break
            if "alias." in line:
                flag = True
            else:
                continue
            if flag:
                name = line.split(":", maxsplit=1)[0].replace("alias.", "")
                wwn = line.split(":", maxsplit=1)[1].strip()
                aliases[name] = wwn
        swt_name = self.lines["switchName"]
        fb_name = self.lines["Fabric Name"]
        self.db.create_tabel(f"alias_cfg_{fb_name}_{swt_name}", "alias_name TEXT, wwn TEXT")
        for key, val in aliases.items():
            self.db.insert_into_table(f"alias_cfg_{fb_name}_{swt_name}", key, val)

    # FIX: Correct split
    def find_switch(self, path_to_file):
        try:
            file_name = fnmatch.filter(os.listdir(f"./uploads/{path_to_file}/"), "*SSHOW_SYS*.txt")[0]
        except IndexError:
            print("Программа не нашла нужный файл")
        else:
            f = open(f"./uploads/{path_to_file}/{file_name}")
        flag = False
        swt_name = self.lines["switchName"]
        fb_name = self.lines["Fabric Name"]
        col = 7
        length = 8
        while True:
            line = f.readline()
            if "Index" in line:
                if "Slot" in line:
                    col = 8
                    length = 9
                flag = True
                lst = line.split()
                temp = "\" TEXT, \"".join(lst)
                self.db.create_tabel(f"switch_{fb_name}_{swt_name}",
                                     f"\"{temp}\" TEXT, \"Port_type\" TEXT, \"WWN\" TEXT, \"Comment\" TEXT")
                continue
            if "=" in line:
                continue
            if flag:
                lst = line.strip().split(maxsplit=col)
                lst_temp = lst[0:col]
                port = "-"
                wwn = "-"
                comment = "-"
                if len(lst) == length:
                    str_temp = lst[col]
                    if "-Port" in str_temp:
                        if "LD" in str_temp:
                            str_temp = str_temp.replace(" ", "_", 1)
                        port = str_temp.split(maxsplit=1)[0]
                        comment = str_temp.split(maxsplit=1)[1]
                        if ":" in comment:
                            wwn = comment[0:23]
                            comment = comment[23::]
                        if len(comment) == 0:
                            comment = "-"
                    else:
                        comment = str_temp
                temp = "', '".join(lst_temp).strip()
                if not self.db.insert_into_table(f'switch_{fb_name}_{swt_name}', temp, port, wwn, comment):
                    break

    def if_for_service(self, line, name):
        global temp
        if "Device type:" in line:
            dev_type = line.strip().split(":", maxsplit=1)[1]
            self.db.update_table(name, "Device_type", dev_type, "PortName", temp[3])
            return
        if "Port Index:" in line:
            port_index = line.strip().split(":", maxsplit=1)[1]
            self.db.update_table(name, "Port_index", port_index, "PortName", temp[3])
            return
        if "PortSymb:" in line:
            port_symb = line.strip().split(":", maxsplit=1)[1]
            self.db.update_table(name, "PortSymb", port_symb, "PortName", temp[3])
            return
        if "NodeSymb:" in line:
            node_symb = line.strip().split(":", maxsplit=1)[1]
            self.db.update_table(name, "NodeSymb", node_symb, "PortName", temp[3])
            return
        if "Device Link speed:" in line:
            speed = line.strip().split(":", maxsplit=1)[1]
            self.db.update_table(name, "Speed", speed, "PortName", temp[3])
            return
        if "Connected through AG:" in line:
            ag = line.strip().split(":", maxsplit=1)[1]
            self.db.update_table(name, "AG", ag, "PortName", temp[3])
            return
        if ";" in line:
            temp = line.strip().split(";", maxsplit=3)
            temp_str = temp[0].split()
            del temp[0]
            temp.insert(0, temp_str[1])
            temp.insert(0, temp_str[0])
            del temp_str
            # ag = "No"
            # port_symb = "-"
            try:
                self.db.insert_into_table(f"'{name}'(Type, Pid, COS, PortName, NodeName)", *temp)
            except Exception:
                pass
            return

    def find_nsshowr(self, path_to_file):
        try:
            file_name = fnmatch.filter(os.listdir(f"./uploads/{path_to_file}/"), "*SSHOW_SERVICE*.txt")[0]
        except IndexError:
            print("Программа не нашла нужный файл")
        else:
            f = open(f"./uploads/{path_to_file}/{file_name}")
        flag = False
        swt_name = self.lines["switchName"]
        fb_name = self.lines["Fabric Name"]
        self.db.create_tabel(f"nsShow-r_{fb_name}_{swt_name}",
                             "Port_index TEXT, Type TEXT, Pid TEXT, COS TEXT, PortName TEXT, "
                             "NodeName TEXT, NodeSymb TEXT, PortSymb TEXT, Device_type TEXT, AG TEXT, Speed TEXT")
        while True:
            line = f.readline()
            if "nsshow -r" in line.strip():
                flag = True
                continue
            if "The Local Name Server has" in line:
                break
            if flag:
                self.if_for_service(line, f"nsShow-r_{fb_name}_{swt_name}")

    def find_nscamshow(self, path_to_file):
        try:
            file_name = fnmatch.filter(os.listdir(f"./uploads/{path_to_file}/"), "*SSHOW_SERVICE*.txt")[0]
        except IndexError:
            print("Программа не нашла нужный файл")
        else:
            f = open(f"./uploads/{path_to_file}/{file_name}")
        flag = False
        swt_name = self.lines["switchName"]
        fb_name = self.lines["Fabric Name"]
        while True:
            line = f.readline()
            if "nscamshow" in line.strip():
                flag = True
                continue
            if "Switch entry for domain " in line:
                break
            if flag:
                if "Switch entry for" in line:
                    num = line.split()[-1]
                    self.db.create_tabel(f"nscamShow_Switch{num}_{fb_name}_{swt_name}",
                                         "Port_index TEXT, Type TEXT, Pid TEXT, COS TEXT, PortName TEXT, "
                                         "NodeName TEXT, NodeSymb TEXT, PortSymb TEXT, Device_type TEXT, AG TEXT, "
                                         "Speed TEXT")
                    continue
                try:
                    self.if_for_service(line, f"nscamShow_Switch{num}_{fb_name}_{swt_name}")
                except Exception:
                    pass

    def find_fabric(self, path_to_file):
        try:
            file_name = fnmatch.filter(os.listdir(f"./uploads/{path_to_file}/"), "*SSHOW_FABRIC*.txt")[0]
        except IndexError:
            print("Программа не нашла нужный файл")
        else:
            f = open(f"./uploads/{path_to_file}/{file_name}")
        flag = False
        swt_name = self.lines["switchName"]
        fb_name = self.lines["Fabric Name"]
        while True:
            line = f.readline()
            if "Switch ID" in line:
                flag = True
                self.db.create_tabel(f"FabricInfo_{fb_name}_{swt_name}",
                                     "Switch TEXT, Id TEXT, WWN TEXT, Enet_IP_Addr TEXT, FC_IP_Addr TEXT, "
                                     "Name TEXT, Principal TEXT")
                continue
            if "The Fabric has" in line:
                break
            if flag:
                if "Switch ID" in line:
                    continue
                principal = "No"
                if ":" in line:
                    data = line.split()
                    if ">" in data[-1]:
                        principal = "Yes"
                    str_sql = "\', \'".join(data)
                    try:
                        self.db.insert_into_table(f"FabricInfo_{fb_name}_{swt_name}", str_sql, principal)
                    except Exception as e:
                        print(e)
                        break

    def find_errshow(self, path_to_file):
        try:
            file_name = fnmatch.filter(os.listdir(f"./uploads/{path_to_file}"), "*SSHOW_SYS*.txt")[0]
        except IndexError:
            print("Программа не нашла нужный файл")
        else:
            f = open(f"./uploads/{path_to_file}/{file_name}")
        flag_cor = False
        micro_flag = False
        swt_name = self.lines["switchName"]
        fb_name = self.lines["Fabric Name"]
        while True:
            line = f.readline()
            if "/fabos/cliexec/porterrshow:" in line:
                flag_cor = True
                self.db.create_tabel(f"PortErrShow_{fb_name}_{swt_name}", "port Text, frames_tx Text, "
                                                                          "frames_rx Text, enc_in Text, crc_err Text, "
                                                                          "crc_g_eof Text, too_shrt, too_long Text, "
                                                                          "bad_eof Text, enc_out Text, disk_c3 Text, "
                                                                          "link_fail Text, loss_sync Text, "
                                                                          "loss_sig Text, frjt Text, fbsy Text, "
                                                                          "c3timeout_tx Text, c3timeout_rx Text, "
                                                                          "pcs_err Text, uncor_err")
                continue
            if flag_cor:
                if "tx" in line:
                    micro_flag = True
                    continue
            if micro_flag:
                data = line.strip().replace(":", "").split()
                if not self.db.insert_into_table(f"PortErrShow_{fb_name}_{swt_name}", *data):
                    break
