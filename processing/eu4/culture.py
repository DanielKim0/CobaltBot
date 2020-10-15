import os
import codecs
from utils import *

class EU4_Parser_Culture:
    def __init__(self):
        self.cultures = dict()
        self.subcultures = dict()
        self.primary = set()

    def parse_file(self, path):
        with codecs.open(path, "r", encoding="iso-8859-1") as f:
            lines = f.readlines()
            curr = None

            for line in lines:
                line = line.rstrip()
                if not line or "#" in line or "}" in line:
                    continue
            
                if "=" in line:
                    if line == line.lstrip():
                        curr = line.split("=")[0].strip()
                        self.cultures[curr] = []
                    else:
                        line = line.lstrip()
                        sub, tag = line.split("=")
                        sub = sub.strip()
                        tag = tag.strip()
                        if sub in ["male_names", "female_names", "dynasty_names", "graphical_culture"]:
                            continue
                        elif sub == "primary":
                            self.primary.add(tag)
                        else:
                            self.cultures[curr].append(sub)
                            self.subcultures[sub] = curr
                        

    def parse_folder(self, path):
        for filename in os.listdir(path):
            self.parse_file(os.path.join(path, filename))
        return self.cultures, self.subcultures, self.primary

if __name__ == "__main__":
    p = EU4_Parser_Culture()
    res = p.parse_folder("../../raw_data/eu4/cultures/")
    print(res)
