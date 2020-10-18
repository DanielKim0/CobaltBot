import os
import codecs
import ast
import re
from abc import ABC, abstractmethod
from utils import *

class EU4_Parser:
    def __init__(self):
        pass

    def parse_folder(self, path):
        data = []
        for filename in os.listdir(path):
            data.append(self.parse_file(os.path.join(path, filename), filename))
        return data

    def parse_file(self, path, filename, return_dict=True):
        with codecs.open(path, "r", encoding="iso-8859-1") as f:
            lines = f.readlines()
            cleaned = self.clean_data(lines)
            if return_dict:
                data = self.create_dict(cleaned)
            else:
                data = self.create_list(cleaned)
            return self.process_file(data, filename)

    @abstractmethod
    def process_file(self, data, filename):
        pass

    def merge(self, item, dupe):
        item = item.rstrip()
        if item[-1] == "\"":
            item = item[:-1]
        if dupe[0] == "\"":
            dupe = dupe[1:]
        return item + "|" + dupe

    def compare_keys(self, curr, new):
        for i in range(min(len(curr), len(new))):
            if ":" in curr[i]:
                return curr[i] == new[i] and "1" not in curr[i]
        return False

    def merge_lines(self, curr, new):
        if len(new) > 2 or new[0] != "NOT:":
            add = []
            for i in range(len(new)):
                if ":" in new[i] and new[i+1] != "{":
                    if new[i] in curr:
                        ind = curr.index(new[i])+1
                        curr[ind] = self.merge(curr[ind], new[i+1])
                    else:
                        add.append(new[i])
                        add.append(new[i+1])
            if add:
                if curr[-1] == "}":
                    curr = curr[:-1] + add + [curr[-1]]
                else:
                    curr = curr + add
        else:
            curr = curr[:-1]
        return curr

    def add_line(self, line):
        for i in range(len(line)):
            if line[i] in ["{", "}", ","]:
                continue
            elif line[i][-1] == ":":
                line[i] = add_quotes(line[i][:-1]) + ":"
            else:
                line[i] = add_quotes(line[i])
        return line

    def clean_data(self, lines):
        data = []
        curr = None
        for line in lines:
            line = self.clean_line(line)

            temp = []
            quotes = 0
            for item in line.split():
                if quotes % 2 == 0:
                    temp.append(item)
                else:
                    temp[-1] += item
                quotes += item.count("\"")
            line = temp

            if not line:
                continue
            if curr:
                if self.compare_keys(curr, line):
                    curr = self.merge_lines(curr, line)
                else:
                    data.append(self.add_line(curr))
                    curr = line
            else:
                curr = line
        if curr:
            data.append(self.add_line(curr))
        return data

    def clean_line(self, line):
        if "#" in line:
            temp = line.split("#")
            if len(temp) < 2:
                return ""
            else:
                temp = temp[0] + "\n"

            # make sure the "#" isn't in quotes
            if temp.count("\"") % 2 == 0:
                line = temp

        line = line.replace("}", " } ").replace("{", " { ")
        while "=" in line:
            line = self.replace_equals(line)
        line = line.lstrip()
        return line

    def replace_equals(self, line):
        ind = line.find("=")
        if ind == -1:
            return line
        
        left = ind - 1
        while left >= 0 and line[left].isspace():
            left -= 1
        right = ind + 1
        while right < len(line) and line[right].isspace():
            right += 1
        return line[:left+1] + ": " + line[right:]

    def create_dict(self, data):
        for i in range(len(data)):
            for j in range(len(data[i])):
                if i+1 < len(data) and ":" in data[i][j] and "}" not in data[i] and "{" not in data[i] and data[i+1][0] == "{":
                    data[i] = data[i] + [data[i+1][0]]
                    data[i+1] = data[i+1][1:]

                if ":" in data[i][j] and data[i][j+1] != "{":
                    data[i][j+1] += ",\n"
                elif data[i][j] == "}":
                    data[i][j] = "},\n"
                elif data[i][j] == "{":
                    data[i][j] = "{\n"
        data = "".join(["".join(i) for i in data])
        data = self.separate(data)
        result = []

        for item in data:
            ind = item.index(":")
            name = item[1:ind-1] # fetch name of date and remove quotes
            if "{" in item:
                con = ast.literal_eval(item[ind+1:])[0]
            else:
                con = item[ind+2:-3]
            result.append([name, con])
        return result

    def separate(self, lines):
        seps = []
        curr = ""
        left = 0
        right = 0

        for line in lines.split("\n"):
            if not line:
                continue
            l = line.count("{")
            r = line.count("}")
            left += l
            right += r
            curr += line + "\n"

            if left == right:
                left = 0
                right = 0
                if curr:
                    seps.append(curr)
                curr = ""
        return seps

    def create_list(self, data):
        temp = []
        for item in data:
            if len(item) > 2:
                i = 0
                while i < len(item):
                    temp.append(item[i:min(i+2, len(item))])
                    i += 2
            else:
                temp.append(item)
        data = temp

        temp = []
        for item in data:
            if item[-1] == "{":
                temp.append("[" + item[0][:-1] + ",")
            elif item[-1] == "}":
                temp.append("],")
            else:
                temp.append("[" + " ".join(item).replace(":", ",") + "],")
        return ast.literal_eval("".join(temp))

    def get_date_index(self, names):
        for i in range(len(names)):
            if names[i][0] == "1": # all dates begin with a year in the 2nd millenia
                return i
        return -1

    def split_file_name(self, filename):
        if "-" in filename:
            a = os.path.splitext(filename)[0].split("-")[0]
            b = "-".join(os.path.splitext(filename)[0].split("-")[1:])
        else:
            a = os.path.splitext(filename)[0].split()[0]
            b = "-".join(os.path.splitext(filename)[0].split()[1:])
        return a.strip(), b.strip()
        
    def check_death_date(self, item):
        if "death_date" in item:
            return(convert_to_date(item["death_date"]) < START_DATE)
        else:
            return False
