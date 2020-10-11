import codecs

class EU4CountyParser:
    def __init__(self):
        pass

    def parse_counties(self, path):
        data = dict()
        with codecs.open(path, "r", encoding="iso-8859-1") as f:
            for line in f.readlines()[1:]:
                line = line.split(";")
                data[int(line[0])] = line[4]
        return data

if __name__ == "__main__":
    p = EU4CountyParser()
    res = p.parse_counties("/home/daniel/Documents/discord/raw_data/eu4/definition.csv")
    print(res)
