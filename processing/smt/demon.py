from requests_html import HTMLSession
import json

class SMT_Demon_Parser:
    def __init__(self, game):
        self.url = "https://aqiu384.github.io/megaten-fusion-tool/"
        self.game = game

    def parse_demon_list(self):
        demon_list = self.url + "?csr=/" + self.game + "/demons"
        session = HTMLSession()
        res = session.get(demon_list)
        res.html.render()
        found = res.html.find("tr.app-smt-demon-list-row")
        return [self.url + self.game + "/demons/" + item.find("td")[2].text for item in found]

    def main(self):
        names = self.parse_demon_list()

if __name__ == "__main__":
    p = SMT_Demon_Parser("smt4")
    p.main()
