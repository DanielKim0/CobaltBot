import os
from datetime import datetime as dt

def add_quotes(string):
    if string[0] != "\"" and string[-1] != "\"":
        return "\"" + string + "\""
    else:
        return string

def transpose(data):
    return list(map(list, zip(*data)))

def convert_to_date(string):
    return dt.strptime(string, "%Y.%m.%d")

def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)

START_DATE = convert_to_date("1444.11.11")