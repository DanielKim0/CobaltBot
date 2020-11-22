import os
import sys
import json
from utils import *
from country import EU4_Parser_Country
from province import EU4_Parser_Province
from diplomacy import EU4_Parser_Diplomacy
from idea import EU4_Parser_Idea
from culture import EU4_Parser_Culture
from religion import EU4_Parser_Religion
from maps import EU4_Parser_Map
from copy import copy
from flag import EU4_Flag_Converter

class EU4_Main:
    def __init__(self, results = "results"):
        self.results = results
        country = EU4_Parser_Country()
        province = EU4_Parser_Province()
        diplomacy = EU4_Parser_Diplomacy()
        culture = EU4_Parser_Culture()
        ideas = EU4_Parser_Idea()
        religion = EU4_Parser_Religion()
        maps = EU4_Parser_Map()
        flag = EU4_Flag_Converter()

        self.country_data = country.parse_folder("../../raw_data/eu4/countries")
        self.tag_list = set(self.country_data.keys())
        self.tags_without_ideas = set(self.country_data.keys())
        self.province_data, self.hre, self.name = province.parse_folder("../../raw_data/eu4/provinces")
        self.diplo_data = diplomacy.parse_folder("../../raw_data/eu4/diplomacy")
        self.culture, self.subculture, self.primary = culture.parse_folder("../../raw_data/eu4/cultures")
        self.religion, self.denoms = religion.parse_folder("../../raw_data/eu4/religions/")
        self.country_ideas = ideas.parse_file("../../raw_data/eu4/ideas/00_country_ideas.txt", "00_country_ideas.txt", False)
        self.group_ideas = ideas.parse_file("../../raw_data/eu4/ideas/zz_group_ideas.txt", "zz_group_ideas.txt", False)
        self.generic_ideas = ideas.parse_file("../../raw_data/eu4/ideas/zzz_default_idea.txt", "zzz_default_idea.txt", False)[0]
        self.basic_ideas = ideas.parse_file("../../raw_data/eu4/ideas/00_basic_ideas.txt", "00_basic_ideas.txt", False)
        self.areas = maps.parse_file("../../raw_data/eu4/map/area.txt")
        self.regions = maps.parse_file("../../raw_data/eu4/map/region.txt")
        self.continents = maps.parse_file("../../raw_data/eu4/map/continent.txt")
        self.flags = flag.process_flags("../../raw_data/eu4/flags", os.path.join(self.results, "images"))
        self.country_names = dict()

    def fetch_country_names(self, data):
        for tag in self.country_data:
            data[tag.lower()] = tag
            country = self.country_data[tag]["country"].lower()
            data[country] = tag
            country = country.split()

            if len(country) > 1:
                if country[0] == "the":
                    data[country[1]] = tag
                if country[1] in ["empire", "khaganate", "khanate", "horde", "order"]:
                    if country[0] not in ["golden", "great"]:
                        add_plural(country[0], tag, data)
                if country[1] == "of":
                    data[country[2]] = tag

        # Hard-code nicknames or common names here
        data["rome"] = "ROM"
        data["timmy"] = "TIM"
        data["timmies"] = "TIM"
        data["hre"] = "HRE"
        data["isles"] = "LOI"
        data["the isles"] = "LOI"
        data["sardinia-piedmont"] = "SPI"
        data["poland-lithuania"] = "PLC"
        data["yokotan"] = "YOK"

        data.pop("teutonics")
        add_plural("otto", "TUR", data)
        add_plural("teuton", "TEU", data)
        add_plural("habsburg", "HAB", data)
        return data

    def fetch_idea_names(self, data):
        for idea in self.basic_ideas:
            data[idea.split("_")[0]] = idea
            data[idea.replace("_", " ")] = idea
            data[idea] = idea
        
        # Nicknames for ideas
        nicknames = ["espionage", "admin", "innovative", "plutocratic", "diplo", 
                    "econ", "expo", "expa", "aristocratic", "qual", "quant"]
        fullnames = ["spy", "administrative", "innovativeness", "plutocracy", "diplomatic", 
                    "economic", "exploration", "expansion", "aristocracy", "quality", "quantity"]

        for i in range(len(nicknames)):
            data[nicknames[i]] = data[fullnames[i] + "_ideas"]
            data[nicknames[i] + " ideas"] = data[fullnames[i] + "_ideas"]
        return data

    def write_names(self, output):
        with open(os.path.join(self.results, output), "w") as f:
            data = dict()
            data = self.fetch_country_names(data)
            data = self.fetch_idea_names(data)
            json.dump(data, f, ensure_ascii=False, indent=4)

    def process_country_names(self):
        # Hardcode discrepancies between country name and in-code country representation here
        self.country_data["KHA"]["country"] = "Mongolia"

        for tag in self.tag_list:
            country = self.country_data[tag]["country"].split()
            for word in ["Empire", "Khaganate", "Khanate", "Horde", "Order"]:
                if word in country[0] and country[0] not in ["Ilkhanate"]:
                    ind = country[0].index(word)
                    country = [country[0][:ind].strip(), word]
                    country = " ".join(country)
                    self.country_data[tag]["country"] = country
                    print(country)
        self.country_names = {tag: self.country_data[tag]["country"] for tag in self.country_data}

    def process_data(self):
        colonial_continents = ["north_america", "south_america", "australia"]
        
        for tag in self.tag_list:
            if "capital" in self.country_data[tag]:
                for key in self.areas:
                    if self.country_data[tag]["capital"] in self.areas[key]:
                        self.country_data[tag]["area"] = key
                        break

                for key in self.continents:
                    if self.country_data[tag]["capital"] in self.continents[key]:
                        self.country_data[tag]["continent"] = key
                        break
                
                # if tech group is western and the capital is in a colonial region, then the nation is a colonial nation
                if self.country_data[tag]["technology_group"] == "western" and self.country_data[tag]["continent"] in colonial_continents:
                    self.country_data[tag]["is_colonial_nation"] = "yes"

                if "area" in self.country_data[tag]:
                    for key in self.regions:
                        if "areas" in self.regions[key] and self.country_data[tag]["area"] in self.regions[key]["areas"]:
                            self.country_data[tag]["region"] = key
                            break
                
                self.country_data[tag]["hre"] = self.hre[int(self.country_data[tag]["capital"])]
                self.country_data[tag]["capital_name"] = self.name[int(self.country_data[tag]["capital"])]
                
            if "primary_culture" in self.country_data[tag]:
                primary = self.country_data[tag]["primary_culture"]
                self.country_data[tag]["culture_group"] = self.subculture[primary]
            if "religion" in self.country_data[tag]:
                self.country_data[tag]["religion_group"] = self.denoms[self.country_data[tag]["religion"]]
            if "add_government_reform" in self.country_data[tag]:
                self.country_data[tag]["has_reform"] = self.country_data[tag]["add_government_reform"]

            if tag in self.province_data:
                self.country_data[tag].update(self.province_data[tag])
                self.country_data[tag]["present"] = True
            else:
                self.country_data[tag]["present"] = False

            if tag in self.diplo_data:
                self.country_data[tag].update(self.diplo_data[tag])

    def clean_data(self):
        self.country_data.pop("REB")
        self.country_data.pop("NAT")
        self.country_data.pop("PIR")

        defunct = ["leader", "change_estate_land_share"]
        for tag in self.country_data:
            to_pop = []
            for key in self.country_data[tag]:
                if not self.country_data[tag][key] or key in defunct:
                    to_pop.append(key)

            if "dev_tax" in self.country_data[tag]:
                self.country_data[tag]["dev_total"] = self.country_data[tag]["dev_tax"] + \
                    self.country_data[tag]["dev_production"] + self.country_data[tag]["dev_manpower"]

            if "has_reform" in self.country_data[tag]:
                self.country_data[tag]["feudal"] = "yes"
                to_pop.append("has_reform")
            else:
                self.country_data[tag]["feudal"] = "no"

            for key in to_pop:
                self.country_data[tag].pop(key)

    def parse_variable_idea_value(self, data):
        final = []
        do_not_multiply = ["republican_tradition", "inflation_reduction", "yearly_corruption", 
            "army_tradition", "navy_tradition", "monthly_fervor_increase", "global_autonomy", 
            "devotion", "hostile_attrition"]

        for item in data:
            if "+" not in item[1] and "%" not in item[1]:
                if "." in item[1]:
                    if item[0] not in do_not_multiply:
                        item[1] = str(float(item[1]) * 100) + "%"
                if "-" not in item[1]:
                    item[1] = "+" + item[1]
            item[0] = self.parse_variable_helper(item[0])
            if item[1] != "+yes":
                final.append(item[1] + " " + item[0])
            else:
                final.append(item[0])

        final = "\n".join(final)
        # Hardcoded string replacements
        final = final.replace("Ae", "Aggressive Expansion")
        final = final.replace("Nationalism", "Seperatism")
        return final

    def parse_variable_idea(self, name, data):
        if name in ["tradition", "ambition"]:
            field = name.capitalize()
        else:
            field = self.parse_variable_helper(name, ["name"])
            field += ": " + self.parse_variable_helper(data[name + "_name"], [data["tag"].lower()])
        return field, self.parse_variable_idea_value(data[name])

    def parse_development(self, data):
        if "dev_total" not in data:
            return [], []
        message = str(data["dev_total"]) + " (" + str(data["dev_tax"]) + "/" + \
            str(data["dev_production"]) + "/" + str(data["dev_manpower"]) + ")"
        return "Total Development", message

    def parse_culture(self, data):
        if "primary_culture" not in data:
            return [], []
        message = ""
        if "culture_group" in data:
            message = "Culture Group: " + self.parse_variable_helper(data["culture_group"], ["group"]) + "\n"
        message += "Primary Culture: " + self.parse_variable_helper(data["primary_culture"]) + "\n"
        if "add_accepted_culture" in data:
            message += "Accepted Cultures: " + self.parse_variable_helper(data["add_accepted_culture"]) + "\n"
        return "Culture", message[:-1]

    def parse_capital(self, data):
        message = "Capital: " + str(data["capital"]) + " (" + data["capital_name"] + ")\n"
        message += "Region: " + self.parse_variable_helper(data["region"], ["region"]) + "\n"
        message += "Area: " + self.parse_variable_helper(data["area"], ["area"]) + "\n"
        message += "Continent: " + data["continent"]
        return "Capital", message

    def parse_religion(self, data):
        if "religion" not in data:
            return [], []
        if data["religion"] == "buddhism":
            message = "Primary Religion: Theravada\n"
        elif data["religion"] == "shamanism":
            message = "Primary Religion: Fetishist\n"
        else:
            message = "Primary Religion: " + self.parse_variable_helper(data["religion"]) + "\n"
        message += "Religious Group: " + self.parse_variable_helper(data["religion_group"]) + "\n"
        if "religious_school" in data:
            message += "Religious School: " + self.parse_variable_helper(data["religious_school"], ["school"]) + "\n"
        if "unlock_cult" in data:
            message += "Fetishist Cults: " + self.parse_variable_helper(data["unlock_cult"], ["cult"]) + "\n"
        return "Religion", message[:-1]

    def parse_government(self, data):
        ranks = ["Duchy", "Kingdom", "Empire"]
        message = "Government Type: " + self.parse_variable_helper(data["government"]) + "\n"
        if "add_government_reform" in data:
            message += "Government Reform: " + self.parse_variable_helper(data["add_government_reform"]) + "\n"
        if "government_rank" in data:
            message += "Government Rank: " + ranks[int(data["government_rank"]) - 1] + "\n"
        if "feudal" in data:
            message += "Feudal: Yes\n"
        else:
            message += "Feudal: No\n"
        return "Government", message[:-1]

    def parse_leader_short(self, key, data):
        if key not in data:
            return [], []
        data[key] = {k.lower(): v for k, v in data[key].items()}
        field = self.parse_variable_helper(key) + " Stats"
        message = data[key]["adm"] + "/" + data[key]["dip"] + "/" + data[key]["mil"]
        return field, message
    
    def parse_leader_full(self, key, data):
        if key not in data:
            return [], []
        field, message = self.parse_leader_short(key, data)
        field = self.parse_variable_helper(key)
        message = "Stats: " + message + "\n"

        name = data[key]["name"]
        if "dynasty" in data[key]:
            name += " " + data[key]["dynasty"]
        message = "Name: " + name + "\n" + message

        if "birth_date" in data[key]:
            message += "Age: " + calculate_age(data[key]["birth_date"]) + " years old\n"
        if "add_" + key + "_personality" in data:
            message += "Traits: " + self.parse_variable_helper(data["add_" + key + "_personality"], ["personality"]) + "\n"

        return field, message[:-1]

    def parse_variable_helper(self, item, prefix_suffix = []):
        if len(item) == 3 and item.isupper():
            if item not in ["ADM", "DIP", "MIL"]:
                return item + " (" + self.country_names[item] + ")"
            else:
                return item
        result = []
        for text in item.split("|"):
            text = text.split("_")
            if text[0] in prefix_suffix:
                text = text[1:]
            if text[-1] in prefix_suffix:
                text = text[:-1]
            text = " ".join([i.capitalize() for i in " ".join(text).split(" ")])
            result.append(text)
        return ", ".join(result)

    def parse_variable(self, key, data):
        if key not in data:
            return [], []
        key_fluff = ["reform", "dev", "add", "set"]
        value_fluff = ["reform", "area", "group"]

        result_key = self.parse_variable_helper(key, key_fluff)
        if type(data[key]) == list:
            result_text = ", ".join([tag + " (" + self.country_names[tag] + ")" for tag in data[key]])
        else:
            result_text = self.parse_variable_helper(str(data[key]), value_fluff)
        return result_key, result_text

    def add_parse(self, result, embed):
        if result[0] and result[1]:
            if type(result[0]) == list:
                embed["fields"].extend(result[0])
                embed["messages"].extend(result[1])     
            else:
                embed["fields"].append(result[0])
                embed["messages"].append(result[1])

    def format_basic_idea(self, data):
        embed = {"title": "", "fields": [], "messages": []}
        embed["title"] = self.parse_variable_helper(data[0])
        self.add_parse((self.parse_variable_helper(data[1][0]), self.parse_variable_helper(data[1][1])), embed)

        if data[3][0] == "trigger":
            start, end = 4, 11
        else:
            start, end = 3, 10

        for i in range(start, end):
            embed["fields"].append("Idea " + str(i - start + 1) + ": " + self.parse_variable_helper(data[i][0]))
            embed["messages"].append(self.parse_variable_idea_value(data[i][1:]))
        return embed

    def format_idea(self, data):
        embed = {"title": "", "fields": [], "messages": [], "image_path": ""}
        embed["title"] = data["tag"] + ": " + data["country"]
        if "tradition" in data:
            self.add_parse(self.parse_variable_idea("tradition", data), embed)
            for i in range(1, 8):
                self.add_parse(self.parse_variable_idea("idea_" + str(i), data), embed)
            self.add_parse(self.parse_variable_idea("ambition", data), embed)
        else:
            self.add_parse(("Error", "No ideas found for this tag!"), embed)
        
        # Temporary solution for images: store them in files and then upload them to discord on call.
        embed["image_path"] = os.path.join(self.flags, data["tag"] + ".png")
        return embed

    def format_important(self, data, embed):
        dependencies = ["vassal", "overlord", "tributary", "hegemon", "guaranteeing", 
                        "guarantor", "junior", "senior", "alliance"]
        self.add_parse(self.parse_leader_short("monarch", data), embed)
        self.add_parse(self.parse_development(data), embed)
        self.add_parse(self.parse_religion(data), embed)
        for key in dependencies:
            self.add_parse(self.parse_variable(key, data), embed)
        return embed
        
    def format_full(self, data, embed):
        if "Monarch Stats" in embed["fields"]:
            ind = embed["fields"].index("Monarch Stats")
            embed["fields"].pop(ind)
            embed["messages"].pop(ind)
        
        for key in ["monarch", "heir", "queen"]:
            self.add_parse(self.parse_leader_full(key, data), embed)
        self.add_parse(self.parse_government(data), embed)
        self.add_parse(self.parse_culture(data), embed)
        
        # Parsing of other variables that aren't already covered in functions
        other = ["province_count", "historical_friend", "historical_rival"]
        for key in other:
            self.add_parse(self.parse_variable(key, data), embed)
        if "present" not in data or data["present"] != True:
            self.add_parse(("Present in 1444", "No"), embed)
        else:
            self.add_parse(("Present in 1444", "Yes"), embed)
        return embed

    def write_data(self):
        create_folder(self.results)
        create_folder(os.path.join(self.results, "ideas"))
        create_folder(os.path.join(self.results, "important"))
        create_folder(os.path.join(self.results, "full"))

        for tag in self.country_data:
            path_idea = os.path.join(self.results, "ideas", tag + ".json")
            path_important = os.path.join(self.results, "important", tag + ".json")
            path_full = os.path.join(self.results, "full", tag + ".json")

            embed = self.format_idea(self.country_data[tag])
            with open(path_idea, "w") as f:
                json.dump(embed, f)
            if "tradition" not in self.country_data[tag]:
                embed = {"title": "", "fields": [], "messages": [], "image_path": embed["image_path"]}

            with open(path_important, "w") as f:
                json.dump(self.format_important(self.country_data[tag], embed), f)
            with open(path_full, "w") as f:
                json.dump(self.format_full(self.country_data[tag], embed), f)

        for idea in self.basic_ideas:
            path = os.path.join(self.results, "ideas", idea + ".json")
            with open(path, "w") as f:
                json.dump(self.format_basic_idea(self.basic_ideas[idea]), f)

    def add_idea(self, idea, tag):
        idea_num = 0
        for item in idea[1:]:
            if item[0] in ["trigger"]:
                continue
            elif item[0] in ["start"]:
                self.country_data[tag]["tradition"] = item[1:]
            elif item[0] in ["bonus"]:
                self.country_data[tag]["ambition"] = item[1:]
            else:
                idea_num += 1
                self.country_data[tag]["idea_" + str(idea_num)] = item[1:]
                self.country_data[tag]["idea_" + str(idea_num) + "_name"] = item[0]

    def parse_basic_ideas(self):
        self.basic_ideas = {self.basic_ideas[i][0]: self.basic_ideas[i] for i in range(len(self.basic_ideas))}

    def parse_condition_tag(self, condition, idea):
        if condition[0] in ["tag", "TAG"]:
            for tag in condition[1].split("|"):
                self.add_idea(idea, tag)
                self.tags_without_ideas.remove(tag)
        else:
            self.parse_condition_tag(condition[1], idea)

    def verify_condition(self, condition, idea, tag):
        if condition[0] not in ["OR", "NOT", "AND"] and type(condition[1]) == list:
            condition = condition[1]

        if condition[0] == "OR":
            or_valid = False
            for cond in condition[1:]:
                if self.verify_condition(cond, idea, tag):
                    or_valid = True
            if not or_valid:
                return False

        elif condition[0] == "NOT":
            for cond in condition[1:]:
                if self.verify_condition(cond, idea, tag):
                    return False
        elif condition[0] == "AND":
            for cond in condition[1:]:
                if not self.verify_condition(cond, idea, tag):
                    return False
        else:
            key, values = condition
            values = values.split("|")
            key = key.lower()
            if key in self.country_data[tag] and not self.country_data[tag][key] in values:
                return False
            if key not in self.country_data[tag] and key != "dynasty":
                return False
        return True

    def parse_condition(self, condition, idea, tag):
        if self.verify_condition(condition, idea, tag):
            self.add_idea(idea, tag)
            self.tags_without_ideas.remove(tag)

    def assign_ideas(self):
        tags = set()
        group_ideas = []
        for tag in ["MGE", "SCA", "NAT", "PIR", "REB"]:
            self.tags_without_ideas.remove(tag)

        for idea in self.country_ideas:
            trigger = idea[3][1]
            if len(trigger) > 2:
                group_ideas.append(idea)
            else:
                self.parse_condition_tag(trigger, idea)

        for idea in group_ideas + self.group_ideas:
            trigger = idea[3][1]
            for tag in copy(self.tags_without_ideas):
                self.parse_condition(trigger, idea, tag)

        for tag in self.tags_without_ideas:
            self.add_idea(self.generic_ideas, tag)

    def main(self):
        self.process_country_names()
        self.process_data()
        self.assign_ideas()
        self.parse_basic_ideas()
        self.clean_data()
        self.write_data()
        self.write_names("names.json")
        
if __name__ == "__main__":
    p = EU4_Main("/home/daniel/Documents/discord/processing/eu4/results")
    p.main()
