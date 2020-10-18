import os
import codecs
import ast
import re
from utils import *
from parser import EU4_Parser

class EU4_Parser_Map:
    def __init__(self):
        self.region = dict()
        self.area = dict()

    def parse_file(self, path):
        with codecs.open(path, "r", encoding="iso-8859-1") as f:
            lines = f.readlines()
            convert = []

            for line in lines:
                line = line.strip().split("#")[0]
                if line and "color = {" not in line:
                    if "=" in line:
                        line = line.split(" =")
                        line[0] = add_quotes(line[0])
                        line = " =".join(line)
                    elif "}" not in line:
                        line = line.split()
                        for i in range(len(line)):
                            line[i] = add_quotes(line[i])
                        line = ", ".join(line)
                        line = line +  ", "
                    convert.append(line)

            convert = "\n".join(convert).replace(" =", ": ").replace("}", "},")
            convert = ast.literal_eval("{" + convert + "}")
            return convert

if __name__ == "__main__":
    p = EU4_Parser_Map()
    res = p.parse_file("../../raw_data/eu4/map/continent.txt")
    print(res)
