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
from map import EU4_Parser_Map
from copy import copy

class EU4_Main:
    def __init__(self, results = "results"):
        country = EU4_Parser_Country()
        province = EU4_Parser_Province()
        diplomacy = EU4_Parser_Diplomacy()
        culture = EU4_Parser_Culture()
        ideas = EU4_Parser_Idea()
        religion = EU4_Parser_Religion()
        maps = EU4_Parser_Map()

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
        self.results = results

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

        for tag in self.country_data:
            to_pop = []
            for key in self.country_data[tag]:
                if not self.country_data[tag][key]:
                    to_pop.append(key)
                if "base_tax" in self.country_data[tag]:
                    self.country_data[tag]["dev_total"] = self.country_data[tag]["dev_tax"] + \
                        self.country_data[tag]["dev_production"] + self.country_data[tag]["dev_manpower"]
            for key in to_pop:
                self.country_data[tag].pop(key)

    def write_data(self):
        create_folder(self.results)
        # for tag in self.country_data:
        #     if 

    def add_idea(self, idea, tag):
        idea_num = 0
        self.country_data[tag]["idea"] = True
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
        self.process_data()
        self.assign_ideas()
        self.clean_data()
        self.write_data()

if __name__ == "__main__":
    p = EU4_Main()
    p.main()

