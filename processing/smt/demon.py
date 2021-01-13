from requests_html import HTMLSession
import json
import os
from utils import *
from collections import defaultdict

class SMT_Demon_Parser:
    """Class that handles parsing website data for SMT demons.

    Attributes:
        url (str): the main url to the website.
        game (str): the game whose data this parser is parsing.
        persona (bool): whether this game is a Persona game or not.
        session (HTMLSession): websession for making requests.
        results (str): path to the folder containing the resulting parsed data."""
    
    def __init__(self, game, results):
        """Method that creates the necessary folders and initializes variables."""

        self.url = "https://aqiu384.github.io/megaten-fusion-tool/"
        self.game = game
        self.persona = self.game == "mib" or self.game[0] == "p"
        self.session = HTMLSession()
        self.results = os.path.join(results, game)
        create_folder(self.results)
        create_folder(os.path.join(self.results, "demons"))
        create_folder(os.path.join(self.results, "fusions"))
        create_folder(os.path.join(self.results, "fissions"))

    def render_html(self, link, script=None):
        """Wrapper that renders the HTML of a link, possibly running a JS script."""

        res = self.session.get(link)
        if script:
            res.html.render(script=script)
        else:
            res.html.render()
        return res

    def extract_evolutions(self, res):
        """Method that extracts evolution data from a demon's stats page."""

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
        """Method that extracts all text from a table, given the class of the tag it's wrapped around."""

        data = res.html.find(cla)
        if not data:
            return
        return [[item.text for item in data[0].find("thead")[0].find("tr")[-1].find("th")], 
                [item.text for item in data[0].find("td")]]

    def parse_demon_list(self):
        """Method that fetches links to each individual demon's stats page."""

        if self.persona:
            describer = "personas"
        else:
            describer = "demons"

        demon_list = self.url + "?csr=/" + self.game + "/" + describer
        res = self.render_html(demon_list)
        found = res.html.find("tr.app-smt-demon-list-row")
        return [[item.find("td")[2].text, self.url + self.game + "/" + describer + "/" + item.find("td")[2].text] for item in found]

    def get_demon_stats(self, res, name):
        """Method that fetches a given demon's base stats and processes them."""

        stats = [[], []]
        data = [item.text for item in res.html.find("app-demon-stats")[0].find("thead")[0].find("tr")[0].find("th")][0].split()
        
        stats[0].append("Name")
        stats[1].append(name)
        stats[0].append("Level")
        stats[1].append(data[1])
        if self.persona:
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
        """Method that gets all of the info about a demon and processes it."""

        res = self.render_html(link)
        stats = self.get_demon_stats(res, name)
        resists = self.extract_table_text(res, "app-demon-resists")
        inherits = self.extract_table_text(res, "app-demon-inherits")

        skills = self.extract_table_text(res, "app-demon-skills")
        skills[1] = split_list(skills[1], len(skills[0]))
        for i in range(len(skills[1])):
            if len(skills[1][i][3].split(".")) > 1:
                skills[1][i][3] = skills[1][i][3].split(".")[0] + "."

        results = {"stats": stats, "resist": resists, "skills": skills, "inherits": inherits}
        return results

    def get_demon_fissions(self, link):
        """Method that fetches a particular demon's fissions from its page and parses them."""

        data = []
        script = """
            () => {
                var navs = document.getElementsByClassName("nav");
                var elem = navs[navs.length-1];
                if (elem.hasAttribute("colspan") && elem.getAttribute("colspan") == 7) {
                    elem.click();
                }

                var navs = document.getElementsByClassName("nav");
                var elem = navs[navs.length-1];
                if (elem.hasAttribute("colspan") && elem.getAttribute("colspan") == 7) {
                    elem.click();
                }

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
        
        if not data or (len(data) == 1 and len(data[0]) == 1):
            return {"fissions": {}, "special": False}

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
        """Method that fetches a particular demon's fusions from its page and parses them."""

        data = []
        res = self.render_html(link)
        trs = res.html.find("app-smt-fusions")[0].find("tbody")[-1].find("tr")
        for tr in trs:
            data.append([item.text for item in tr.find("td")])

        if not data or (len(data) == 1 and len(data[0]) == 1):
            return {}

        fusions = dict()
        for item in data:
            demon1 = item[3]
            demon2 = item[6]
            fusions[demon1] = demon2
        return fusions

    def main(self):
        """Main method that fetches, parses, and stores data on all demons from a game."""

        links = self.parse_demon_list()
        names = []
        for link in links:
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
    games = ["smt3", "smt4", "smt4f", "p3p", "p4g", "p5r"]
    for game in games:
        print("Game: " + game)
        p = SMT_Demon_Parser(game, "results")
        p.main()
        print()
