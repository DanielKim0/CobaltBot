from datetime import datetime as dt

class Country:
    def __init__(self):
        self.gov = None
        self.gov_reform = None
        self.gov_rank = None
        self.mercantilism = 10
        self.tech_group = None
        self.religion = None
        self.pri_culture = None
        self.acc_culture = None
        self.capital = None
        self.nat_focus = None
        self.professionalism = None
        self.rival = None # historical rival
        self.friend = None # historical friend
        self.religious_school = None
        self.cult = None

class Ruler:
    def __init__(self):
        self.name = None
        self.dynasty = None
        self.personality = None
        self.regent = False
        self.adm = 0
        self.dip = 0
        self.mil = 0

class General:
    def __init__(self):
        self.admiral = False
        self.fire = 0
        self.shock = 0
        self.manuever = 0
        self.siege = 0
        self.personality = None
        self.ruler = False

def add_quotes(string):
    if string[0] != "\"" and string[-1] != "\"":
        return "\"" + string + "\""
    else:
        return string

def transpose(data):
    return list(map(list, zip(*data)))

def convert_to_date(string):
    return dt.strptime(string, "%Y.%m.%d")

def check_death_date(item):
    if "death_date" in item:
        return(convert_to_date(item["death_date"]) < START_DATE)
    else:
        return False


START_DATE = convert_to_date("1444.11.11")
