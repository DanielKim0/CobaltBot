import os
import codecs
import ast
import re
from utils import *
from parser import EU4_Parser
import datetime

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

    def process_file(self, data):
        # get relevant data and 1444 royalty
        data = list(map(list, zip(*data)))
        return data

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
    result = p.parse_file("../../raw_data/eu4/countries/KOR - Korea.txt")
    # result = p.parse_file("../../raw_data/eu4/countries/FRA - France.txt")
    print(result)
