import os
import codecs
import ast
import re
from utils import *
from parser import EU4_Parser

class EU4_Idea_Parser(EU4_Parser):
    def __init__(self):
        super().__init__()
        self.idea_dict = dict()

    def parse_separate(self, data):
        result = []
        for part in data:
            part = part.replace("{", "{\n")
            part = part.replace("}", "\n}")
            result.append(self.parse_separate_helper(part))
        return result

    def parse_separate_helper(self, part):
        name = part[:part.index(":")]
        idea = self.separate(part.splitlines(True)[1:-1])
        idea = [i.rstrip() for i in idea]

        for i in range(len(idea)):
            if "{" in idea[i]:
                idea[i] = self.parse_separate_helper(idea[i])
        return [name, idea]

    def process_file(self, data, filename):
        for idea in data:
            name = idea[0]
            desc = idea[1]

            if "free: yes" in desc:
                desc.remove("free: yes")
            
            for i in range(len(desc)):
                if desc[i][0] not in ["start", "bonus"]:
                    if desc[i][1]:
                        self.idea_dict[desc[i][0]] = desc[i][1]
                    else:
                        if desc[i][0] in self.idea_dict:
                            desc[i][1] = self.idea_dict[desc[i][0]]
                        else:
                            raise ValueError("Idea not found in idea dictionary.")
        return data

p = EU4_Idea_Parser()
res = p.parse_file("/home/daniel/Documents/discord/raw_data/eu4/ideas/00_country_ideas.txt", "zz_group_ideas.txt")
# res = p.parse_file("/home/daniel/Documents/discord/raw_data/sample.txt", "sample.txt")
