import os
import sys
import json
from country import EU4_Parser_Country
from county import EU4_Parser_County
from diplomacy import EU4_Parser_Diplomacy
from idea import EU4_Parser_Idea
from culture import EU4_Parser_Culture
from copy import copy

class EU4_Main:
    def __init__(self):
        country = EU4_Parser_Country()
        # county = EU4_Parser_County()
        # diplomacy = EU4_Parser_Diplomacy()
        culture = EU4_Parser_Culture()
        ideas = EU4_Parser_Idea()

        self.country_data = country.parse_folder("../../raw_data/eu4/countries")
        self.tag_list = set(self.country_data.keys())
        self.tags_without_ideas = set(self.country_data.keys())
        # self.county_data = county.parse_folder("../../raw_data/eu4/")
        # self.diplo_data = diplomacy.parse_folder("../../raw_data/eu4/")
        self.culture, self.subculture, self.primary = culture.parse_folder("../../raw_data/eu4/cultures")
        self.country_ideas = ideas.parse_file("../../raw_data/eu4/ideas/00_country_ideas.txt", "00_country_ideas.txt", False)
        self.group_ideas = ideas.parse_file("../../raw_data/eu4/ideas/zz_group_ideas.txt", "zz_group_ideas.txt", False)
        self.basic_ideas = ideas.parse_file("../../raw_data/eu4/ideas/00_basic_ideas.txt", "00_basic_ideas.txt", False)

    def parse_culture_data(self):
        pass
        # for tag in self.tag_list:
        #     if "primary_culture" in self.country_data[tag]:
        #         primary = self.country_data[tag]["primary_culture"]
        #         for key in self.culture:
        #             if primary in self.culture[key]:
        #                 self.country_data[tag]["culture_group"] = key

    def parse_idea(self, idea):
        # TODO
        return idea

    def parse_condition_tag(self, condition, idea):
        if "tag" in condition[0] or "TAG" in condition[0]:
            tags = condition[0].split(": ")[1]
            for tag in tags.split("|"):
                self.country_data[tag] = self.parse_idea(idea)
                self.tags_without_ideas.remove(tag)
        else:
            self.parse_condition_tag(condition[0][1], idea)

    def verify_condition(self, condition, idea, tag):
        for item in condition:
            if item[0] == "OR":
                or_valid = False
                for cond in item[1]:
                    if self.parse_condition([cond], idea, tag):
                        or_valid = True
                if not or_valid:
                    return False
            elif item[0] == "NOT":
                if self.parse.condition([cond], idea, tag):
                    return False
            elif item[0] == "AND":
                for cond in item[1]:
                    if not self.parse_condition([cond], idea, tag):
                        return False
            else:
                key, values = item.split(": ")
                values = values.split("|")
                if key in self.country_data[tag] and not self.country_data[tag][key] in values:
                    return False
                if key not in self.country_data[tag] and key != "dynasty":
                    return False
        return True

    def parse_condition(self, condition, idea, tag):
        if self.verify_condition(condition, idea, tag):
            self.country_data[tag] = self.parse_idea(idea)
            self.tags_without_ideas.remove(tag)

    def assign_ideas(self):
        tags = set()
        group_ideas = []
        for i in self.country_ideas:
            idea = i[1]
            trigger = idea[2][1]
            if len(trigger[0][1]) > 1:
                group_ideas.append(i)
            else:
                self.parse_condition_tag(trigger, idea)

        for i in self.group_ideas + group_ideas:
            print(i)
            idea = i[1]
            trigger = idea[2][1]
            for tag in copy(self.tags_without_ideas):
                self.parse_condition(trigger, idea, tag)

    def main(self):
        self.parse_culture_data()
        self.assign_ideas()
        # print(self.tags_without_ideas)

if __name__ == "__main__":
    p = EU4_Main()
    p.main()
