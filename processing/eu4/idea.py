import os
import codecs
import ast
import re
from utils import *
from parser import EU4_Parser

class EU4_Parser_Idea(EU4_Parser):
    def __init__(self):
        super().__init__()
        self.idea_dict = dict()

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

if __name__ == "__main__":
    p = EU4_Parser_Idea()
    res = p.parse_file("../../raw_data/eu4/diplomacy/African_alliances.txt", "alliances.txt", False)
    print(res)
