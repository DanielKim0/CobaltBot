import os
import codecs
import ast
import re
from abc import ABC, abstractmethod
from utils import *

class EU4_Parser:
    def __init__(self):
        # TODO
        pass

    def parse_folder(self, path):
        data = []
        for filename in os.listdir(path):
            data.append(self.parse_file(os.path.join(path, filename), filename))
        return data

    def parse_file(self, path, filename, return_dict=True):
        with codecs.open(path, "r", encoding="iso-8859-1") as f:
            lines = f.readlines()
            separated = self.separate(lines)
            if return_dict:
                data = self.parse_separate_dict(separated)
            else:
                data = self.parse_separate_list(separated)
            return self.process_file(data, filename)

    @abstractmethod
    def process_file(self, data, filename):
        pass

    def parse_separate_dict(self, data):
        bracket = False
        result = []
        for line in data:
            if not bracket and "{" in line:
                bracket = True
            if bracket:
                result.append(self.parse_bracket(line))
            else:
                result.append(self.parse_bracketless(line))
        return transpose(result)

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

    def parse_separate_list(self, data):
        result = []
        for part in data:
            part = part.replace("{", "{\n")
            part = part.replace("}", "\n}")
            result.append(self.parse_separate_list_helper(part))
        return result

    def parse_separate_list_helper(self, part):
        name = part[:part.index(":")]
        idea = self.separate(part.splitlines(True)[1:-1])
        idea = [i.rstrip() for i in idea]

        for i in range(len(idea)):
            if "{" in idea[i]:
                idea[i] = self.parse_separate_list_helper(idea[i])
        return [name, idea]

    def separate(self, lines):
        seps = []
        curr = ""
        key = None
        edited = False

        left = 0
        right = 0

        for line in lines:
            line = self.clean_line(line)
            if not line:
                continue
            l = line.count("{")
            r = line.count("}")

            left += l
            right += r

            # below if statements used for combining same non-date entries together
            # some entries are left dangling if the loop had just submitted an entry
            split = line.split(": ")
            if len(split) < 2:
                curr_key = None
            else:
                curr_key = split[0]

            if (curr_key == key) and (curr_key is not None) and ("1" not in curr_key):
                if edited:
                    curr = curr.rstrip() + "|" + split[1]
                else:
                    seps[-1] = seps[-1].rstrip() + "|" + split[1]
            else:
                curr += line
                edited = True
            key = curr_key

            if left == right:
                left = 0
                right = 0
                if curr:
                    seps.append(curr)
                curr = ""
                edited = False
        return seps

    def clean_line(self, line):
        while '  ' in line:
            line = line.replace('  ', ' ')
        if "#" in line:
            line = line.split("#")
            if len(line) < 2:
                return ""
            else:
                line = line[0] + "\n"
        line = line.replace("}", " }").replace("{", "{ ")
        while "=" in line:
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
