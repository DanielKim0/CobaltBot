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

class LeagueCog(CobaltCog):
    def __init__(self):
        super().__init__()
        load_dotenv()
        self.token = os.getenv("RIOT_TOKEN")
        self.header = {"User-Agent": "Linux Mint:CobaltBot:v0.0.1"}
        self.lock = Lock()
        self.call_repeatedly()

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

    @commands.command(name="mmr", description="", aliases=[], usage="")
    @check_valid_command
    async def get_mmr(self, ctx, name: str):
        name = name.replace(" ", "+")
        req = requests.get("https://na.whatismymmr.com/api/v1/summoner?name=" + name, headers=self.header)
        text = ast.literal_eval(req.text.replace("null", "\"\"").replace("true", "True").replace("false", "False"))

        if "error" in text:
            await ctx.send("Error: invalid username!")
            return 

        warn = False
        results = []
        for queue in text:
            results.append([[], []])

            results[-1][0] = [queue + " mmr", queue + " %"]

            if text[queue]["avg"]:
                average = str(text[queue]["avg"])
                if text[queue]["warn"]:
                    average += "*"
                    warn = True
                average += " ± " + str(text[queue]["err"])
                results[-1][1].append(average)
                results[-1][1].append(await self.calculate_dist(text[queue]["avg"], queue))
            else:
                results[-1][1] = ["N/A", "N/A"]

        table = ""
        for item in results:
            table += tabulate(item, tablefmt="grid") + "\n"
        table = "```\n" + name + "'s stats\n\n" + table + "\n"
        if warn:
            table += "* Insufficient data, proceed with caution.\n"
        table += "```"
        await ctx.send(table)

    def get_info(self, name):
        pass

if __name__ == "__main__":
    l = LeagueCog()
    l.get_mmr("catast999")
