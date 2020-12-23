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
        """Method that processes an idea file and parses idea data, including requirements, from that file."""
        
        for idea in data:
            if ["free", "yes"] in idea:
                idea.remove(["free", "yes"])

            for i in range(1, len(idea)):
                if idea[i][0] not in ["start", "bonus", "trigger", "ai_will_do", "category"]:
                    if len(idea[i]) > 1:
                        self.idea_dict[idea[i][0]] = idea[i][1:]
                    else:
                        if idea[i][0] in self.idea_dict:
                            for item in self.idea_dict[idea[i][0]]:
                                idea[i].append(item)
                        else:
                            raise ValueError("Idea not found in idea dictionary.")
        return list(data)

if __name__ == "__main__":
    p = EU4_Parser_Idea()
    res = p.parse_file("../../raw_data/eu4/ideas/zz_group_ideas.txt", "zz_group_ideas.txt", False)
    for item in res:
        print(item)
