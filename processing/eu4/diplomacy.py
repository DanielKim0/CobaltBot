import os
import codecs
import ast
import re
from utils import *
from parser import EU4_Parser
from datetime import datetime as dt

class EU4_Parser_Diplomacy(EU4_Parser):
    def __init__(self):
        super().__init__()
        self.relations = dict()

    def add_tag(self, tag):
        self.relations[tag] = {
            "overlord": [],
            "hegemon": [], # for tributary
            "tributary": [],
            "vassal": [],
            "guaranteeing": [],
            "guarantor": [],
            "alliance": []
        }

    def process_file(self, data, filename):
        for relation in data:
            if len(relation[1]) >= 4:
                start = convert_to_date(relation[1][-2].split(": ")[1])
                end = convert_to_date(relation[1][-1].split(": ")[1])

                if start <= START_DATE and end >= START_DATE:
                    first = relation[1][-4].split(": ")[1]
                    second = relation[1][-3].split(": ")[1]
                    if first not in self.relations:
                        self.add_tag(first)
                    if second not in self.relations:
                        self.add_tag(second)

                    if relation[0] == "vassal": 
                        self.relations[first]["vassal"].append(second)
                        self.relations[second]["overlord"].append(first)
                    elif relation[0] == "alliance":
                        self.relations[first]["alliance"].append(second)
                        self.relations[second]["alliance"].append(first)
                    elif relation[0] == "dependency":
                        self.relations[first]["tributary"].append(second)
                        self.relations[second]["hegemon"].append(first)
                    elif relation[0] == "guarantee":
                        self.relations[first]["guaranteeing"].append(second)
                        self.relations[second]["guarantor"].append(first)
                    else:
                        print(relation[0])

    def parse_folder(self, path):
        for filename in os.listdir(path):
            self.parse_file(os.path.join(path, filename), filename, False)
        return self.relations

if __name__ == "__main__":
    p = EU4_Parser_Diplomacy()
    res = p.parse_folder("../../raw_data/eu4/diplomacy/")
    print(res)
