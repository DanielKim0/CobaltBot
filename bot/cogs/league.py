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

class LeagueCog(CobaltCog):
    def __init__(self):
        super().__init__()
        load_dotenv()
        self.token = os.getenv("RIOT_TOKEN")
        self.header = {"User-Agent": "Linux Mint:CobaltBot:v0.0.1"}
        self.dist = self.get_dist()
        # self.schedule_dist()

    def calculate_dist(self, mmr, queue):
        mmr = str(round(mmr, -1))
        return self.dist[queue][mmr]/self.dist[queue]["total"]

    def get_dist(self):
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
        return dist

    def schedule_dist(self):
        async def dist_job(self):
            while True:
                dist = self.get_dist()
                await asyncio.sleep(3600)

        loop = asyncio.get_event_loop()
        task = loop.create_task(self.dist_job())

        try:
            loop.run_until_complete(task)
        except asyncio.CancelledError:
            with open('err.log', 'a') as f:
                f.write("Async league cog distribution update cancelled!")

    @commands.command(name="mmr", description="", aliases=[], usage="")
    @check_valid_command
    async def get_mmr(self, ctx, name: str):
        name = name.replace(" ", "+")
        req = requests.get("https://na.whatismymmr.com/api/v1/summoner?name=" + name, headers=self.header)
        text = ast.literal_eval(req.text.replace("null", "\"\"").replace("true", "True").replace("false", "False"))

        results = []
        for queue in text:
            results.append([[], []])
            results[-1][0].append(queue)
            if text[queue]["avg"]:
                dist = self.calculate_dist(text[queue]["avg"], queue)
            else:
                dist = "N/A"
            results[-1][1].append(dist)

        table = ""
        for item in results:
            table += tabulate(item, tablefmt="grid") + "\n"
        await ctx.send("```\n" + name + "'s stats\n\n" + table + "```")

    def get_info(self, name):
        pass

if __name__ == "__main__":
    l = LeagueCog()
    l.get_mmr("catast999")
