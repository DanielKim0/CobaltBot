import os
import codecs
import sqlite3
import ast
import re
from utils import *

class EU4_Country_Parser:
    def __init__(self):
        # TODO
        pass

    def parse_file(self, path):
        with codecs.open(path, "r", encoding="iso-8859-1") as f:
            lines = f.readlines()
            separated = self.separate(lines)
            names = []
            data = []
            for line in separated[0]:
                name, datum = self.parse_line(line)
                names.append(name)
                data.append(datum)
            for line in separated[1]:
                name, datum = self.parse_bracket(line)
                names.append(name)
                data.append(datum)
        return names, data

    def separate(self, lines):
        seps = [[], []]
        curr = ""
        bracket = False

        left = 0
        right = 0

        for line in lines:
            line = self.clean_line(line)
            if not line:
                continue
            l = line.count("{")
            r = line.count("}")

            if l > 0 and not bracket:
                bracket = True

            if not bracket:
                seps[0].append(line)
            else:
                left += l
                right += r
                curr += line

                if left == right:
                    left = 0
                    right = 0
                    seps[1].append(curr)
                    curr = ""
        return seps

    def clean_line(self, line):
        # BROKEN?
        while '  ' in line:
            line = line.replace('  ', ' ')
        if "#" in line:
            line = line.split("#")
            if len(line) < 2:
                return ""
            else:
                line = line[0]
        line = line.replace("}", " }").replace("{", "{ ")
        # replace equal sign with ": " here
        line = self.replace_equals(line)
        line = line.lstrip()
        return line

    def replace_equals(self, line):
        ind = line.find("=")
        if ind == -1:
            return line
        
        left = ind - 1
        while line[left].isspace() and left >= 0:
            left -= 1
        right = ind + 1
        while line[right].isspace() and right < len(line):
            right += 1
        return line[:left+1] + ": " + line[right:]

    def parse_line(self, line):
        line = line.strip()
        line = line.split(": ")
        return line[0], line[1]

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

p = EU4_Parser()
