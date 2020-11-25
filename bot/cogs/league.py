import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from cobalt import CobaltCog, check_valid_command
import json
from tabulate import tabulate
import requests
import ast

class LeagueCog(CobaltCog):
    def __init__(self):
        load_dotenv()
        self.token = os.getenv("RIOT_TOKEN")
        self.header = {"User-Agent": "Linux:CobaltBot:v0.0.1"}
        self.dist = self.get_dist()
        # self.schedule_dist()

    def calculate_dist(self, mmr, queue):
        mmr = round(mmr, -1)
        return [self.dist[queue][mmr], self.dist[queue][total]]

    def get_dist(self):
        website = "https://na.whatismymmr.com/api/v1/distribution"
        r = ast.literal_eval(requests.get(website, headers=self.header).text)
        dist = dict()
        
        for queue in r:
            queue = queue.lower()
            dist[queue] = dict()
            keys = [str(i) for i in sorted([int(i) for i in r[queue].keys()])]
            total = 0

            for key in keys:
                if r[queue][key] == 0 and not dist[queue]:
                    continue
                if not dist[queue]:
                    r[queue]["min"] = key
                total += r[queue][key]
                dist[queue][key] = total
            r[queue]["max"] = keys[-1]
            r[queue]["total"] = total       
        return dist

    def schedule_dist(self):
        async def dist_job(self):
            while True:
                dist = self.get_dist() # race condition?
                await asyncio.sleep(3600)

        loop = asyncio.get_event_loop()
        task = loop.create_task(self.dist_job())

        try:
            loop.run_until_complete(task)
        except asyncio.CancelledError:
            # Add to err.log!
            pass

    def get_mmr(self, name):
        name = name.replace(" ", "+")
        r = requests.get("https://na.whatismymmr.com/api/v1/summoner?name=" + name, headers=self.header)
        print(r.text)

    def get_info(self, name):
        pass

if __name__ == "__main__":
    l = LeagueCog()