import os
import codecs
import ast
import re
from utils import *
from parser import EU4_Parser
from datetime import datetime as dt

class EU4_Parser_Province(EU4_Parser):
    def __init__(self):
        super().__init__()
        self.country_dict = dict()

    def add_tag(self, tag):
        self.country_dict[tag] = {
            "province_count": 0,
            "dev_tax": 0,
            "dev_production": 0,
            "dev_manpower": 0,
            "hre": False, # capital is in the HRE
        }

    def process_file(self, data, filename):
        if data:
            data = self.update_province_info(data)
            self.get_province_info(data)
    
    def get_province_info(self, data):
        if "owner" in data:
            tag = data["owner"]
            if data["owner"] not in self.country_dict:
                self.add_tag(tag)
            self.country_dict[tag]["province_count"] += 1
            self.country_dict[tag]["dev_tax"] += int(data["base_tax"])
            self.country_dict[tag]["dev_production"] += int(data["base_production"])
            self.country_dict[tag]["dev_manpower"] += int(data["base_manpower"])
            if "capital" in data and len(data["add_core"].split("|")) == 1 and data["hre"] == "yes":
                self.country_dict[tag]["hre"] = True

    def update_province_info(self, data):
        prov = {data[i][0]: data[i][1] for i in range(len(data))}

        data = transpose(data)
        names = data[0]
        ind = self.get_date_index(names)
        if ind == -1:
            return prov
        names = names[ind:]
        data = data[1][ind:]

        for i in range(len(names)):
            if names[i][0] == "1":
                date = convert_to_date(names[i])
                if date > START_DATE:
                    break
                for key in data[i]:
                    if key == "add_core" and "add_core" in prov:
                        prov[key] = prov[key] + "|" + data[i][key]
                    else:
                        prov[key] = data[i][key]
            else:
                prov[names[i]] = data[i]
        return prov

    def parse_folder(self, path):
        for filename in os.listdir(path):
            self.parse_file(os.path.join(path, filename), filename)
        return self.country_dict

if __name__ == "__main__":
    p = EU4_Parser_Province()
    res = p.parse_folder("../../raw_data/eu4/provinces")
    # res = p.parse_file("../../raw_data/eu4/provinces/1213 - Shoa.txt", "4510 - Shorkot.txt")
    print(p.country_dict)