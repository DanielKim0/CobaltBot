import os
import codecs
import ast
import re
from utils import *

class EU4_Idea_Parser:
    def __init__(self):
        #TODO
        pass

    def parse_file(self, path):
        with codecs.open(path, "r", encoding="iso-8859-1") as f:
            lines = f.readlines()
            separated = self.separate(lines)
            print(separated)



p = EU4_Idea_Parser()
p.parse_file("/home/daniel/Documents/discord/raw_data/eu4/ideas/zz_group_ideas.txt")