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
        create_folder(self.results)
        create_folder(os.path.join(self.results, "demons"))
        create_folder(os.path.join(self.results, "fusions"))
        create_folder(os.path.join(self.results, "fissions"))

    def render_html(self, link, script=None):
        res = self.session.get(link)
        if script:
            res.html.render(script=script)
        else:
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
        return [[item.find("td")[2].text, self.url + self.game + "/demons/" + item.find("td")[2].text] for item in found]

    def get_demon_stats(self, link):
        res = self.render_html(link)
        stats = self.extract_table_text(res, "app-demon-stats")
        resists = self.extract_table_text(res, "app-demon-resists")
        skills = self.extract_table_text(res, "app-demon-skills")
        skills[1] = split_list(skills[1], len(skills[0]))
        results = {"stats": stats, "resist": resists, "skills": skills}
        if self.game in ["smt4f"]:
            results["affinities"] = self.extract_table_text(res, "app-demon-inherits")
        return results

    def get_demon_fissions(self, link):
        data = []
        script = """
            () => {
                var navs = document.getElementsByClassName("nav");
                var elem = navs[navs.length-1];
                if (elem.hasAttribute("colspan") && elem.getAttribute("colspan") == 7) {
                    elem.click();
                }
            }
        """
        res = self.render_html(link, script=script)

        trs = res.html.find("app-smt-fission-table")[0].find("tbody")[-1].find("tr")
        for tr in trs:
            data.append([item.text for item in tr.find("td")])
        
        special = len(data[0]) == 4
        if special:
            return {"fissions": [data[i][-1] for i in range(len(data))], "special": special}
        
        fissions = defaultdict(list)
        for item in data:
            demon1 = item[3]
            demon2 = item[6]
            fissions[demon1].append(demon2)
            fissions[demon2].append(demon1)
        return {"fissions": fissions, "special": special}

    def get_demon_fusions(self, link):
        data = []
        res = self.render_html(link)
        trs = res.html.find("app-smt-fusions")[0].find("tbody")[-1].find("tr")
        for tr in trs:
            data.append([item.text for item in tr.find("td")])

        fusions = dict()
        for item in data:
            demon1 = item[3]
            demon2 = item[6]
            fusions[demon1] = demon2
        return fusions

    def main(self):
        links = self.parse_demon_list()
        names = []
        for link in links[:1]:
            name, link = link
            print(name)
            names.append(name)
            stats = self.get_demon_stats(link)
            fissions = self.get_demon_fissions(link + "/fissions")
            fusions = self.get_demon_fusions(link + "/fusions")

            with open(os.path.join(self.results, "demons", name + ".json"), "w") as f:
                f.write(json.dumps(stats))
            with open(os.path.join(self.results, "fissions", name + ".json"), "w") as f:
                f.write(json.dumps(fissions))
            with open(os.path.join(self.results, "fusions", name + ".json"), "w") as f:
                f.write(json.dumps(fusions))

        with open(os.path.join(self.results, "demon_names.json"), "w") as f:
            f.write(json.dumps(names))

if __name__ == "__main__":
    p = SMT_Demon_Parser("smt4", "results")
    p.main()
