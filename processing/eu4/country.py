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

    def process_file(self, data, filename):
        result = []
        names = data[0]
        data = data[1]
        ind = self.get_date_index(names)
        
        info = self.get_country_info(names[:ind], data[:ind], filename)
        if ind != -1:
            rulers = self.get_current_rulers(names[ind:], data[ind:])
        else:
            rulers = []
        return [info, rulers]

    def get_date_index(self, names):
        for i in range(len(names)):
            if names[i][0] == "1": # all dates begin with a year in the 2nd millenia
                return i
        return -1

    def get_country_info(self, names, data, filename):
        data = {names[i]: data[i] for i in range(len(data))}
        tag, country = os.path.splitext(filename)[0].split(" - ")
        data["tag"] = tag
        data["country"] = country
        return data
        
    def get_current_rulers(self, names, data):
        monarch = None
        heir = None
        consort = None
        generals = []

        for i in range(len(names)):
            date = convert_to_date(names[i])
            if date > START_DATE:
                break
            
            if "monarch" in data[i] and not check_death_date(data[i]["monarch"]):
                monarch = data[i]["monarch"]
                heir = None
                consort = None
            if "heir" in data[i] and not check_death_date(data[i]["heir"]):
                heir = data[i]["heir"]
            if "consort" in data[i] and not check_death_date(data[i]["consort"]):
                consort = data[i]["consort"]
            if "leader" in data[i] and not check_death_date(data[i]["leader"]):
                generals.append(data[i]["leader"])
            
            rulers = [monarch, heir, consort]
            for i in range(len(rulers)):
                if rulers[i] and "leader" in rulers[i]:
                    generals.append(rulers[i]["leader"])
                    rulers[i].pop("leader")
        return monarch, heir, consort, generals

if __name__ == "__main__":
    p = EU4_Parser_Country()
    # result = p.parse_file("../../raw_data/eu4/countries/ALB - Albania.txt", "ALB - Albania.txt")
    # result = p.parse_file("../../raw_data/eu4/countries/FRA - France.txt", "FRA - France.txt")
    result = p.parse_file("../../raw_data/eu4/countries/KOR - Korea.txt", "KOR - Korea.txt")
    print(result)
