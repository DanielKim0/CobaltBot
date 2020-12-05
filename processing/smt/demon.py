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
        self.results = os.path.join(results, game)
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

    def extract_evolutions(self, res):
        data = res.html.find("app-fusion-entry-table")
        result = [[], []]

        for item in data:
            header = item.find("table")[0].find("thead")[0].find("tr")[0].find("th")[0].text
            text = item.find("table")[0].find("tbody")[0].find("tr")[0].find("td")[-1].text
            if header in ["Evolves From", "Evolves To"]:
                result[0].append(header)
                result[1].append(text)
        return result

    def extract_table_text(self, res, cla):
        data = res.html.find(cla)[0]
        return [[item.text for item in data.find("thead")[0].find("tr")[-1].find("th")], 
                [item.text for item in data.find("td")]]

    def parse_demon_list(self):
        demon_list = self.url + "?csr=/" + self.game + "/demons"
        res = self.render_html(demon_list)
        found = res.html.find("tr.app-smt-demon-list-row")
        return [[item.find("td")[2].text, self.url + self.game + "/demons/" + item.find("td")[2].text] for item in found]

    def get_demon_stats(self, res, name):
        stats = [[], []]
        data = [item.text for item in res.html.find("app-demon-stats")[0].find("thead")[0].find("tr")[0].find("th")][0].split()
        
        stats[0].append("Name")
        stats[1].append(name)
        stats[0].append("Level")
        stats[1].append(data[1])
        if self.game == "mib" or self.game[0] == "p":
            stats[0].append("Arcana")
        else:
            stats[0].append("Race")
        stats[1].append(data[2])

        evos = self.extract_evolutions(res)
        stats[0].extend(evos[0])
        stats[1].extend(evos[1])

        data = self.extract_table_text(res, "app-demon-stats")
        stats[0].extend(data[0])
        stats[1].extend(data[1])
        return stats

    def get_demon_info(self, link, name):
        res = self.render_html(link)
        stats = self.get_demon_stats(res, name)
        resists = self.extract_table_text(res, "app-demon-resists")
        skills = self.extract_table_text(res, "app-demon-skills")
        skills[1] = split_list(skills[1], len(skills[0]))
        for i in range(len(skills[1])):
            if len(skills[1][i][3].split(". ")) > 1:
                skills[1][i][3] = skills[1][i][3].split(". ")[0] + "."
        results = {"stats": stats, "resist": resists, "skills": skills}
        if self.game in ["smt4f"]:
            results["affinities"] = self.extract_table_text(res, "app-demon-inherits")
        # if self.game in ["smt3"]:
        #     results["inherits"]
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
        for link in links[:10]:
            name, link = link
            print(name)
            names.append(name.lower())
            stats = self.get_demon_info(link, name)
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
    # games = ["smt3", "smt4", "smt4f"]
    games = ["smt3"]
    for game in games:
        print("Game: " + game)
        p = SMT_Demon_Parser(game, "results")
        p.main()
        print()
