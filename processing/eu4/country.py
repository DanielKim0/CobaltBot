import os
import codecs
import ast
import re
from utils import *
from parser import EU4_Parser
from datetime import datetime as dt

class EU4_Parser_Country(EU4_Parser):
    def __init__(self):
        super().__init__()

    def parse_folder(self, path):
        data = dict()
        for filename in os.listdir(path):
            country = self.parse_file(os.path.join(path, filename), filename)
            data[country["tag"]] = country
        return data

    def process_file(self, data, filename):
        result = []
        data = transpose(data)
        names = data[0]
        data = data[1]
        ind = self.get_date_index(names)
        
        if ind != -1:
            info = self.get_country_info(names[:ind], data[:ind], filename)
            rulers = self.get_current_rulers(names[ind:], data[ind:])
            info = self.apply_country_changes(names[ind:], data[ind:], info)
        else:
            info = self.get_country_info(names, data, filename)
            rulers = []
        
        if rulers:
            info["monarch"] = rulers[0]
            info["heir"] = rulers[1]
            info["consort"] = rulers[2]
        return info

    def apply_country_changes(self, names, data, info):
        for i in range(len(names)):
            date = convert_to_date(names[i])
            if date > START_DATE:
                break

            for key in data[i]:
                if key in ["clear_scripted_personalities", "add_ruler_personality", "monarch", "heir", "consort"]:
                    continue
                info[key] = data[i][key]

        return info

    def get_date_index(self, names):
        for i in range(len(names)):
            if names[i][0] == "1": # all dates begin with a year in the 2nd millenia
                return i
        return -1

    def get_country_info(self, names, data, filename):
        data = {names[i]: data[i] for i in range(len(data))}
        tag = os.path.splitext(filename)[0].split("-")[0]
        country = "-".join(os.path.splitext(filename)[0].split("-")[1:])

        data["tag"] = tag.strip()
        data["country"] = country.strip()
        return data
        
    def get_current_rulers(self, names, data):
        monarch = None
        heir = None
        consort = None

        for i in range(len(names)):
            date = convert_to_date(names[i])
            if date > START_DATE:
                break
            
            if "monarch" in data[i] and not check_death_date(data[i]["monarch"]):
                monarch = data[i]["monarch"]
                
                if "add_ruler_personality" in data[i]:
                    monarch["add_ruler_personality"] = data[i]["add_ruler_personality"]
                heir = None
                consort = None
            if "heir" in data[i] and not check_death_date(data[i]["heir"]):
                heir = data[i]["heir"]
            if "consort" in data[i] and not check_death_date(data[i]["consort"]):
                consort = data[i]["consort"]

        return monarch, heir, consort

if __name__ == "__main__":
    p = EU4_Parser_Country()
    result = p.parse_file("../../raw_data/eu4/countries/SRH - Sirhind.txt", "SRH - Sirhind.txt")
    # result = p.parse_file("../../raw_data/eu4/countries/MUG - Mughal.txt", "MUG - Mughal.txt")
    print(result)
