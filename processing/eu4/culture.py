import os
from utils import *
from parser import EU4_Parser

class EU4_Parser_Culture(EU4_Parser):
    def __init__(self):
        super().__init__()
        self.cultures = dict()
        self.primary = dict()

    def process_file(self, data, filename):
        for item in data:
            current = item[0]
            self.cultures[item[0]] = []
            for subculture in item:
                for i in subculture:
                    if i[0] not in ["male_names", "female_names", "graphical_culture", "dynasty_names"] and len(i[0]) > 1:
                        self.cultures[current].append(i[0])
                        for j in i:
                            for final in j:
                                if "primary" in final:
                                    tag = final.split(": ")[1]
                                    self.primary[tag] = "True"

    def parse_folder(self, path):
        for filename in os.listdir(path):
            self.parse_file(os.path.join(path, filename), filename, False)
        return self.cultures, self.primary

if __name__ == "__main__":
    p = EU4_Parser_Culture()
    res = p.parse_folder("../../raw_data/eu4/cultures/")
    print(res)
