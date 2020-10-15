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
        # tag is the blank of everything in the list
        self.relations[tag] = {
            "overlord": [],
            "hegemon": [], # for tributary
            "tributary": [],
            "vassal": [],
            "guaranteeing": [],
            "guarantor": [],
            "alliance": [],
            "senior": [],
            "junior": [],
            "marriage": []
        }

    def process_file(self, data, filename):
        for relation in data:
            if "start_date" in relation[1]:
                start = convert_to_date(relation[1]["start_date"])
                end = convert_to_date(relation[1]["end_date"])

                if start <= START_DATE and end >= START_DATE:
                    first = relation[1]["first"]
                    second = relation[1]["second"]
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
                    elif relation[0] == "union":
                        self.relations[first]["junior"].append(second)
                        self.relations[second]["senior"].append(first)
                    elif relation[0] == "royal_marriage":
                        self.relations[first]["marriage"].append(second)
                        self.relations[second]["marriage"].append(first)

    def parse_folder(self, path):
        for filename in os.listdir(path):
            self.parse_file(os.path.join(path, filename), filename)
        return self.relations

if __name__ == "__main__":
    p = EU4_Parser_Diplomacy()
    res = p.parse_folder("../../raw_data/eu4/diplomacy/")
    print(res)
