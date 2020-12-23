import os
import codecs
from utils import *
from parser import EU4_Parser

class EU4_Parser_Religion(EU4_Parser):
    def __init__(self):
        self.religion = dict()
        self.denoms = dict()

    def process_file(self, data, filename):
        """Method that parses religious data from a file, retrieving groups and denominations."""
        
        for item in data:
            self.religion[item[0]] = set()
            for i in item[1:]:
                if i[1][0] in ["color", "icon", "flags_with_emblem_percentage"]:
                    self.religion[item[0]].add(i[0])
                    self.denoms[i[0]] = item[0]

    def parse_folder(self, path):
        """Wrapper that parses every file in a folder."""

        for filename in os.listdir(path):
            self.parse_file(os.path.join(path, filename), filename, False)
        return self.religion, self.denoms

if __name__ == "__main__":
    p = EU4_Parser_Religion()
    res = p.parse_folder("../../raw_data/eu4/religions/")
    print(res)
