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
    """Cog that handles league functionality.

    Attributes:
        header (dict): json header to make to WhatIsMyMMR calls.
        lock (threading.Lock): lock to protect against race conditions when saving mmr dist data.
        champs (dict): maps cass champ ids to their names."""

    def __init__(self):
        super().__init__()
        load_dotenv()
        self.header = {"User-Agent": "Raspberry Pi 4:CobaltBot:v1.0.0"}
        self.lock = Lock()
        self.get_dist()
        self.cass_setup()
        self.call_repeatedly()
        self.champs = self.champ_setup()

    def champ_setup(self):
        """Method that fetches champions and their IDs using cass."""
        champs = dict()
        for champ in cass.get_champions():
            champs[champ.id] = champ.name
        return champs

    def cass_setup(self):
        cass.set_riot_api_key(os.getenv("RIOT_TOKEN"))
        cass.set_default_region("NA")

    def call_repeatedly(self):
        """Wrapper that calls get_dist every hour."""

        stopped = Event()

        def loop(self):
            while not stopped.wait(3600):
                print("Fetching league dist")
                self.get_dist()

        Thread(target=loop, args = [self]).start()    
        return stopped.set

    async def calculate_dist(self, mmr, queue):
        """Method that calculates your place in a given queue's MMR distribution."""

        mmr = str(round(mmr, -1))
        with self.lock:
            percent = self.dist[queue][mmr]/self.dist[queue]["total"]
        return "top " + str(round((1 - percent) * 100, 2)) + "%"

    def get_dist(self):
        """Method that fetches and stores league MMR distribution data."""

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

        with self.lock:
            self.dist = dist

    async def get_mmr(self, name):
        """Method that requests data from WhatIsMyMMR and parses it into a usable format."""

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
                interval = str(text[queue]["err"])
                if not interval:
                    interval = "0"
                average += " ± " + interval
                results[1].append(average)
                results[1].append(await self.calculate_dist(text[queue]["avg"], queue))
            else:
                results[1].extend(["N/A", "N/A"])
        return results, warn

    async def get_cass(self, player):
        """Method that requests summoner data from cass and parses it into a usable format."""

        summ = [["Level", "Solo Rank", "Flex Rank"], []]
        summ[1].append(player.level)

        ranks = dict()
        for item in player.ranks:
            ranks[item.value] = str(player.ranks[item].tier) + " " + str(player.ranks[item].division)

        for queue in ["RANKED_SOLO_5x5", "RANKED_FLEX_SR"]:
            if queue in ranks:
                summ[1].append(ranks[queue])
            else:
                summ[1].append("N/A")

        champs = [["Champ", "Points", "Level"]]
        for master in player.champion_masteries[:5]:
            champs.append([master.champion.name, master.points, master.level])

        return [summ, champs]

    def get_match_player(self, match, id):
        for team in match.teams:
            for p in team.participants:
                if p.summoner.id == id:
                    return p

    async def get_last_match(self, player):
        """Method that requests last match data from cass and parses it into a usable format."""

        data = [["Queue", "Champ", "KDA", "CS", "Vision"], []]
        summ = None
        num = 0

        while not summ and num < 10:
            match = player.match_history[num]
            summ = self.get_match_player(match, player.id)
            stats = summ.stats
            num += 1

        if not player:
            return None

        data[1].append(match.queue.value)
        data[1].append(self.champs[summ.champion.id])
        data[1].append(str(stats.kills) + "/" + str(stats.deaths) + "/" + str(stats.assists))
        data[1].append(stats.total_minions_killed)
        data[1].append(stats.vision_score)
        return data

    @commands.command(name="league", description="", aliases=[], usage="")
    @check_valid_command
    async def get_stats(self, ctx, name: str):
        """Method that gets a summoner's statistics, makes them into tables, and sends them on discord."""

        player = cass.get_summoner(name=name)
        names = ["User Data", "Champion Data", "MMR Data"]
        results = []

        results.extend(await self.get_cass(player))
        mmr, warn = await self.get_mmr(name)
        results.append(mmr)
        match = await self.get_last_match(player)
        if match:
            names.append("Last Match Stats")
            results.append(match)

        table = ""
        for i in range(len(results)):
            table += names[i] + "\n"
            table += tabulate(results[i], tablefmt="grid") + "\n\n"
        table = "```\n" + name + "'s stats\n\n" + table + "\n"
        if warn:
            table += "* Insufficient data, proceed with caution.\n"
        table += "```"

        await ctx.send(table)
