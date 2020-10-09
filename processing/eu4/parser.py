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

    def parse_file(self, path):
        with codecs.open(path, "r", encoding="iso-8859-1") as f:
            lines = f.readlines()
            separated = self.separate(lines)
            data = []
            for line in separated:
                data.append(self.parse_line(line))
        return self.process_file(data)

    @abstractmethod
    def process_file(self, data):
        pass

    def separate(self, lines):
        seps = []
        curr = ""

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
            curr += line

            if left == right:
                left = 0
                right = 0
                seps.append(curr)
                curr = ""
        return seps

    def clean_line(self, line):
        while '  ' in line:
            line = line.replace('  ', ' ')
        if "#" in line:
            line = line.split("#")
            if len(line) < 2:
                return ""
            else:
                line = line[0]
        line = line.replace("}", " }").replace("{", "{ ")
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