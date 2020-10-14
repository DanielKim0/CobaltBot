import os
import codecs
import ast
import re
from utils import *
from parser import EU4_Parser
from datetime import datetime as dt

class EU4_Parser_County(EU4_Parser):
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
        data = {data[0][i]: data[1][i] for i in range(len(data[0]))}
        tag = data["owner"]
        if data["owner"] not in self.country_dict:
            self.add_tag(tag)
        self.country_dict[tag]["province_count"] += 1
        self.country_dict[tag]["dev_tax"] += int(data["base_tax"])
        self.country_dict[tag]["dev_production"] += int(data["base_production"])
        self.country_dict[tag]["dev_manpower"] += int(data["base_manpower"])
        if "capital" in data and len(data["add_core"].split("|")) == 1 and data["hre"] == "yes":
            self.country_dict[tag]["hre"] = True

    def parse_folder(self, path):
        for filename in os.listdir(path):
            self.parse_file(os.path.join(path, filename), filename)
        return self.country_dict

if __name__ == "__main__":
    p = EU4_Parser_County()
    res = p.parse_file("/home/daniel/Documents/discord/raw_data/eu4/provinces/1-Uppland.txt", "1-Uppland.txt")
    