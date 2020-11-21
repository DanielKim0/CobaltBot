from requests_html import HTMLSession
import json

class SMT_Demon_Parser:
    def __init__(self):
        self.demon_list = "https://aqiu384.github.io/megaten-fusion-tool/?csr=/smt4/demons"

    def parse_demon_list(self):
        session = HTMLSession()
        res = session.get(self.demon_list)
        res.html.render()
        found = res.html.find("tr.app-smt-demon-list-row")
        for item in found:
            print([i.text for i in item.find("td")])

    def main(self):
        self.parse_demon_list()

if __name__ == "__main__":
    p = SMT_Demon_Parser()
    p.main()
