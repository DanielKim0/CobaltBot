import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from cogs.cobalt import CobaltCog, check_valid_command
import json
from tabulate import tabulate
import requests
import ast
import asyncio
from threading import Event, Thread, Lock
import sys
import cassiopeia as cass

class LeagueCog(CobaltCog):
    def __init__(self):
        super().__init__()
        load_dotenv()
        self.header = {"User-Agent": "Linux Mint:CobaltBot:v0.0.1"}
        self.lock = Lock()
        self.get_dist()
        self.cass_setup()
        self.call_repeatedly()

    def cass_setup(self):
        cass.set_riot_api_key(os.getenv("RIOT_TOKEN"))
        cass.set_default_region("NA")

    def call_repeatedly(self):
        stopped = Event()

        def loop(self):
            while not stopped.wait(15):
                self.get_dist()

        Thread(target=loop, args = [self]).start()    
        return stopped.set

    async def calculate_dist(self, mmr, queue):
        mmr = str(round(mmr, -1))
        self.lock.acquire()
        percent = self.dist[queue][mmr]/self.dist[queue]["total"]
        self.lock.release()
        return "top " + str(round((1 - percent) * 100, 2)) + "%"

    def get_dist(self):
        sys.stdout.flush()
        website = "https://na.whatismymmr.com/api/v1/distribution"
        req = requests.get(website, headers=self.header)
        text = ast.literal_eval(req.text)
        dist = dict()
        
        for queue in text:
            dist[queue] = dict()
            keys = [str(i) for i in sorted([int(i) for i in text[queue].keys()])]
            total = 0

            for key in keys:
                if text[queue][key] == 0 and not dist[queue]:
                    continue
                if not dist[queue]:
                    text[queue]["min"] = key
                total += text[queue][key]
                dist[queue][key] = total

            dist[queue]["max"] = keys[-1]
            dist[queue]["total"] = total

        self.lock.acquire()
        self.dist = dist
        self.lock.release()

    async def get_mmr(self, name):
        results = [[], []]
        name = name.replace(" ", "+")
        req = requests.get("https://na.whatismymmr.com/api/v1/summoner?name=" + name, headers=self.header)
        text = ast.literal_eval(req.text.replace("null", "\"\"").replace("true", "True").replace("false", "False"))

        if "error" in text:
            await ctx.send("Error: invalid username!")
            return 

        warn = False
        for queue in text:
            results[0].extend([queue + " mmr", queue + " %"])

            if text[queue]["avg"]:
                average = str(text[queue]["avg"])
                if text[queue]["warn"]:
                    average += "*"
                    warn = True
                average += " ± " + str(text[queue]["err"])
                results[1].append(average)
                results[1].append(await self.calculate_dist(text[queue]["avg"], queue))
            else:
                results[1].extend(["N/A", "N/A"])
        return results, warn

    async def get_cass(self, name):
        summ = [["", "Rank"]]
        player = cass.get_summoner(name=name)
        

        champs = [["name", "points", "level"]]
        for master in player.champion_masteries[:5]:
            champs.append([master.champion,name, master.points, master.level])

        return [summ, champs]

    @commands.command(name="league", description="", aliases=[], usage="")
    @check_valid_command
    async def get_stats(self, ctx, name: str):
        names = ["User Data", "Champion Data", "MMR Data"]
        results = []

        results.extend(await self.get_cass(name))
        mmr, warn = await self.get_mmr(name)
        results.append(mmr)

        table = ""
        for i in range(len(results)):
            table += names[i] + "\n"
            table += tabulate(results[i], tablefmt="grid") + "\n"
        table = "```\n" + name + "'s stats\n\n" + table + "\n"
        if warn:
            table += "* Insufficient data, proceed with caution.\n"
        table += "```"

        await ctx.send(table)

    def get_info(self, name):
        pass
