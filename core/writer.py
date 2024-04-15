from db import Db


class Writer:
    def __init__(self):
        self.db = Db()

    def write_fabric(self, fb_name: str, swt_name: str, workbook) -> None:
        columns = self.db.cur.execute(f"PRAGMA table_info(\"FabricInfo_{fb_name}_{swt_name}\");").fetchall()
        columns = list(map(lambda x: x[1], columns))
        columns = columns[0:4] + columns[5:]
        sql_temp = ", ".join(columns)
        data = self.db.select(f"FabricInfo_{fb_name}_{swt_name}", sql_temp)
        worksheet = workbook.add_worksheet("Fabric")
        for i, val in enumerate(columns):
            worksheet.write(0, i, val)
        for i, row in enumerate(data, start=1):
            for j, val in enumerate(row):
                worksheet.write(i, j, val)

    def write_switches(self, fb_name: str, swt_name: str, workbook) -> None:
        config = self.db.select(f"data_{fb_name}_{swt_name}", "zoning")[0]
        # nsShow
        worksheet = workbook.add_worksheet("nsShow")
        worksheet.write(0, 0, "Name:")
        worksheet.write(0, 1, swt_name)
        worksheet.write(0, 2, "Ports:")
        res = self.db.select(f"switch_{fb_name}_{swt_name}", "Port_type", True, "State = \"Online\"")
        active_port = len(res)
        res = self.db.select(f"switch_{fb_name}_{swt_name}", "Port_type")
        ports = len(res)
        worksheet.write(0, 3, f"{active_port}/{ports}")
        worksheet.write(1, 0, "IP:")
        res = self.db.select(f"FabricInfo_{fb_name}_{swt_name}", "Enet_IP_Addr", True,
                             f"Name = '\"{swt_name}\"' OR Name = '>\"{swt_name}\"'")
        worksheet.write(1, 1, res[0])
        worksheet.write(1, 2, "Config:")
        worksheet.write(1, 3, config)
        data = self.db.select(f"nsShow-r_{fb_name}_{swt_name}", "Pid, PortName")
        alias = []
        for i in range(len(data)):
            try:
                alias_name = self.db.select(f"alias_cfg_{fb_name}_{swt_name}", "alias_name", True,
                                            f"wwn = \"{data[i][1]}\"")
                alias.append(alias_name[0])
            except Exception:
                alias.append(tuple("-"))
        dec = list(map(lambda x: int(x[0::][0][2:4], 16), data))
        for i, val in enumerate(dec, start=3):
            worksheet.write(i, 0, val)
        for i, row in enumerate(data, start=3):
            for j, val in enumerate(row, start=1):
                worksheet.write(i, j, val)
        for i, row in enumerate(alias, start=3):
            for j, val in enumerate(row, start=3):
                worksheet.write(i, j, val)

        # nscamShow
        names_ip = self.db.select(f"FabricInfo_{fb_name}_{swt_name}", "Name, Enet_IP_Addr")
        for i, val in enumerate(names_ip):
            if val[0] == swt_name:
                del names_ip[i]
        res = self.db.select(f"FabricInfo_{fb_name}_{swt_name}", "Switch")
        switch = list(map(lambda x: x[0], res))
        switch = list(map(lambda x: x.replace(":", ""), switch))
        for i, val in enumerate(switch):
            worksheet = workbook.add_worksheet(f"Switch{val}")
            worksheet.write(0, 0, "Name:")
            worksheet.write(0, 1, names_ip[i][0])
            worksheet.write(0, 2, "Ports:")
            res = self.db.select(f"switch_{fb_name}_{swt_name}", "Port_type", True, "State = \"Online\"")
            active_port = len(res)
            res = self.db.select(f"switch_{fb_name}_{swt_name}", "Port_type")
            ports = len(res)
            worksheet.write(0, 3, f"{active_port}/{ports}")
            worksheet.write(1, 0, "IP:")
            worksheet.write(1, 1, names_ip[i][1])
            worksheet.write(1, 2, "Config:")
            worksheet.write(1, 3, config)
            try:
                data = self.db.select(f"nscamShow_Switch{val}_{fb_name}_{swt_name}", "Pid, PortName")
            except Exception:
                pass
            alias = []
            for i in range(len(data)):
                try:
                    alias_name = self.db.select(f"alias_cfg_{fb_name}_{swt_name}", "alias_name", True,
                                                f"wwn = \"{data[i][1]}\"")
                    alias.append(alias_name[0])
                except Exception:
                    alias.append(tuple("-"))
            dec = list(map(lambda x: int(x[0::][0][2:4], 16), data))
            for i, val in enumerate(dec, start=3):
                worksheet.write(i, 0, val)
            for i, row in enumerate(data, start=3):
                for j, val in enumerate(row, start=1):
                    worksheet.write(i, j, val)
            for i, row in enumerate(alias, start=3):
                for j, val in enumerate(row, start=3):
                    worksheet.write(i, j, val)

    def wrtie_zone(self, fb_name: str, swt_name: str, workbook):
        worksheet = workbook.add_worksheet("Zones")
        worksheet.write(0, 0, "Zone")
        worksheet.write(0, 1, "Zone members")
        mycel = self.db.select(f"zone_cfg_{fb_name}_{swt_name}", "*")
        for i, row in enumerate(mycel, start=1):
            for j, val in enumerate(row):
                try:
                    arr = val.split(";")[0::]
                    for k, vval in enumerate(arr):
                        worksheet.write(i, k, vval)
                except Exception:
                    worksheet.write(i, j, val)
