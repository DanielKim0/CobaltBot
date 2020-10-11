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

    def parse_separate(self, data):
        bracket = False
        result = []
        for line in data:
            if not bracket and "{" in line:
                bracket = True
            if bracket:
                result.append(self.parse_bracket(line))
            else:
                result.append(self.parse_bracketless(line))
        return result

    def process_file(self, data, filename):
        result = []
        data = transpose(data)
        print(data)
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

    def parse_bracketless(self, line):
        line = line.strip()
        return line.split(": ")

    def parse_bracket(self, string):
        parts = self.sep_bracket(string)
        for i in range(len(parts)):
            if ":" in parts[i]:
                parts[i] = "\n" + parts[i]
        string = "".join(parts)[1:].replace("}", "\n}\n")
        return self.convert_bracket(self.format_bracket(string))
    
    def sep_bracket(self, string):
        parts = string.split()
        new_parts = []
        quote = False
        for part in parts:
            if quote:
                new_parts[-1] += " " + part
            else:
                new_parts.append(part)

            for i in range(part.count("\"")):
                quote = not quote
        return new_parts

    def format_bracket(self, string):
        lines = string.split("\n")

        result = []
        for line in lines:
            if not line:
                continue
            if line.strip() == "}":
                result.append("},\n")
                continue
            line = line.split(":")
            line[0] = add_quotes(line[0])
            if not(line[1] == "{" or line[1].isnumeric()):
                line[1] = add_quotes(line[1])
            if not (line[1]) == "{":
                line[1] = line[1] + ","
            result.append(": ".join(line) + "\n")
        return "".join(result)

    def convert_bracket(self, bracket):
        ind = bracket.index(":")
        name = bracket[1:ind-1] # fetch name of date and remove quotes
        con = ast.literal_eval(bracket[ind+2:])[0]
        return name, con

if __name__ == "__main__":
    p = EU4_Parser_Country()
    # result = p.parse_file("../../raw_data/eu4/countries/ALB - Albania.txt", "ALB - Albania.txt")
    # result = p.parse_file("../../raw_data/eu4/countries/FRA - France.txt", "FRA - France.txt")
    result = p.parse_file("../../raw_data/eu4/countries/KOR - Korea.txt", "KOR - Korea.txt")
    print(result)
