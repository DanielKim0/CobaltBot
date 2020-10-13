import os
import codecs
import ast
import re
from utils import *
from parser import EU4_Parser
from datetime import datetime as dt

class EU4_Parser_County(EU4_Parser):
    def __init__(self):
        super().__init__()

    def parse_separate(self, lines):
        print(lines)
        pass

    def process_file(self, data, filename):
        pass


if __name__ == "__main__":
    p = EU4_Parser_County()
    res = p.parse_file("/home/daniel/Documents/discord/raw_data/eu4/provinces/1-Uppland.txt", "1-Uppland.txt")
    print(res)
