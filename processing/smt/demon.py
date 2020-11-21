from requests_html import HTMLSession
import json
import os
from utils import *
from collections import defaultdict

class SMT_Demon_Parser:
    def __init__(self, game, results):
        self.url = "https://aqiu384.github.io/megaten-fusion-tool/"
        self.game = game
        self.session = HTMLSession()
        self.results = results
        if not os.path.exists(self.results):
            os.mkdir(self.results)

    def render_html(self, link):
        res = self.session.get(link)
        res.html.render()
        return res

    def extract_table_text(self, res, cla):
        data = res.html.find(cla)[0]
        return [[item.text for item in data.find("thead")[0].find("tr")[-1].find("th")], 
                [item.text for item in data.find("td")]]

    def parse_demon_list(self):
        demon_list = self.url + "?csr=/" + self.game + "/demons"
        res = self.render_html(demon_list)
        found = res.html.find("tr.app-smt-demon-list-row")
        return [self.url + self.game + "/demons/" + item.find("td")[2].text for item in found]

    def get_demon_stats(self, link):
        res = self.render_html(link)
        base = self.extract_table_text(res, "app-demon-stats")
        resistances = self.extract_table_text(res, "app-demon-resists")
        skills = self.extract_table_text(res, "app-demon-skills")
        skills[1] = split_list(skills[1], len(skills[0]))
        results = [base, resistances, skills]
        if self.game in ["smt4f"]:
            results.append(self.extract_table_text(res, "app-demon-inherits"))
        return results

    def get_demon_fissions(self, link):
        data = []
        res = self.render_html(link)
        trs = res.html.find("app-smt-fissions")[0].find("tbody")[-1].find("tr")
        for tr in trs:
            data.append([item.text for item in tr.find("td")])
        
        special = len(data[0]) == 4
        if special:
            return [[data[0] for i in data], special]
        
        fissions = defaultdict(list)
        for item in data:
            demon1 = data[3]
            demon2 = data[6]
            fusions[demon1].append(demon2)
            fusions[demon2].append(demon1)
        return [fissions, special]

    def get_demon_fusions(self, link):
        data = []
        res = self.render_html(link)
        trs = res.html.find("app-smt-fusions")[0].find("tbody")[-1].find("tr")
        for tr in trs:
            data.append([item.text for item in tr.find("td")])\

        fusions = dict()
        for item in data:
            demon1 = data[3]
            demon2 = data[6]
            fusions[demon1] = demon2)
        return fusions

    def main(self):
        links = self.parse_demon_list()
        # stats = self.get_demon_stats(links[0])
        self.get_demon_fusions(links[0] + "/fissions")

if __name__ == "__main__":
    p = SMT_Demon_Parser("smt4", "results")
    p.main()
